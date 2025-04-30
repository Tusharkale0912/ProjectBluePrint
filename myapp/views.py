from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, Cart, CartItem
from .utils import send_otp_to_console, is_email, is_phone_number
import re
import random
from django.utils import timezone
from django.contrib.messages import constants as message_constants

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        otp = request.POST.get('otp')
        resend_otp = request.POST.get('resend_otp') == 'true'

        # If OTP is not provided, this is the first step
        if not otp:
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists')
                return render(request, 'register.html')

            # Check if email/phone already exists
            if User.objects.filter(email=identifier).exists() or \
               UserProfile.objects.filter(phone_number=identifier).exists():
                # Check if the user is partially registered and clean up
                if User.objects.filter(email=identifier).exists():
                    user = User.objects.get(email=identifier)
                    if not user.userprofile.is_email_verified:
                        user.delete()
                elif UserProfile.objects.filter(phone_number=identifier).exists():
                    profile = UserProfile.objects.get(phone_number=identifier)
                    if not profile.is_phone_verified:
                        profile.user.delete()

                # Recheck after cleanup
                if User.objects.filter(email=identifier).exists() or \
                   UserProfile.objects.filter(phone_number=identifier).exists():
                    messages.error(request, 'Email or phone number already registered')
                    return render(request, 'register.html')

            # Create user first
            if is_email(identifier):
                user = User.objects.create_user(
                    username=username,
                    email=identifier,
                    password=password
                )
                profile = UserProfile.objects.create(
                    user=user,
                    is_email_verified=False
                )
            else:
                user = User.objects.create_user(
                    username=username,
                    password=password
                )
                profile = UserProfile.objects.create(
                    user=user,
                    phone_number=identifier,
                    is_phone_verified=False
                )

            # Generate and send OTP
            new_otp = profile.generate_otp()
            if new_otp is None:
                messages.error(request, 'Too many OTP requests. Please try again later.')
                # Delete the user if OTP generation fails
                user.delete()
                return render(request, 'register.html')
                
            send_otp_to_console(identifier, new_otp)
            
            # Store user ID and identifier in session for verification
            request.session['pending_verification_user_id'] = user.id
            request.session['pending_verification_identifier'] = identifier
            
            messages.success(request, f'OTP sent! Check console (Development mode). Your OTP is: {new_otp}')
            return render(request, 'register.html', {'show_otp': True, 'identifier': identifier})

        else:
            # Handle resend OTP request
            if resend_otp:
                user_id = request.session.get('pending_verification_user_id')
                stored_identifier = request.session.get('pending_verification_identifier')
                
                if not user_id or not stored_identifier:
                    messages.error(request, 'Registration data not found. Please try again.')
                    return render(request, 'register.html')
                
                try:
                    user = User.objects.get(id=user_id)
                    profile = user.userprofile
                    
                    # Generate a new OTP
                    new_otp = profile.generate_otp()
                    if new_otp is None:
                        messages.error(request, 'Too many OTP requests. Please try again later.')
                        return render(request, 'register.html', {'show_otp': True, 'identifier': stored_identifier})
                    
                    send_otp_to_console(stored_identifier, new_otp)
                    messages.success(request, f'New OTP sent! Check console (Development mode). Your OTP is: {new_otp}')
                    return render(request, 'register.html', {'show_otp': True, 'identifier': stored_identifier})
                    
                except (User.DoesNotExist, UserProfile.DoesNotExist):
                    messages.error(request, 'User not found. Please try registering again.')
                    # Clear session data
                    if 'pending_verification_user_id' in request.session:
                        del request.session['pending_verification_user_id']
                    if 'pending_verification_identifier' in request.session:
                        del request.session['pending_verification_identifier']
                    return render(request, 'register.html')
            
            # Verify OTP
            user_id = request.session.get('pending_verification_user_id')
            stored_identifier = request.session.get('pending_verification_identifier')
            
            if not user_id or not stored_identifier:
                messages.error(request, 'Registration data not found. Please try again.')
                return render(request, 'register.html')
                
            # Verify that the identifier matches what was used during registration
            if identifier != stored_identifier:
                messages.error(request, 'Identifier mismatch. Please use the same email/phone used during registration.')
                return render(request, 'register.html', {'show_otp': True, 'identifier': stored_identifier})

            try:
                user = User.objects.get(id=user_id)
                profile = user.userprofile
                
                # Debug information
                print(f"Verifying OTP: {otp}")
                print(f"Stored OTP hash: {profile.otp_hash}")
                print(f"OTP created at: {profile.otp_created_at}")
                
                # Verify the OTP
                verification_result = profile.verify_otp(otp)
                print(f"Verification result: {verification_result}")

                if verification_result:
                    # Mark verification as complete
                    if is_email(stored_identifier):
                        profile.is_email_verified = True
                    else:
                        profile.is_phone_verified = True
                    profile.save()

                    # Clear session data
                    del request.session['pending_verification_user_id']
                    del request.session['pending_verification_identifier']

                    # Debugging logs to confirm OTP verification flow
                    print("OTP verification successful. Redirecting to login page.")
                    messages.success(request, 'Verification successful! Please log in.')
                    return redirect('login')
                else:
                    # Check if OTP is expired
                    if profile.otp_created_at and timezone.now() > profile.otp_created_at + timezone.timedelta(minutes=5):
                        messages.error(request, 'OTP has expired. Please request a new one.')
                    else:
                        messages.error(request, 'Invalid OTP. Please try again.')
                    return render(request, 'register.html', {'show_otp': True, 'identifier': stored_identifier})

            except (User.DoesNotExist, UserProfile.DoesNotExist):
                messages.error(request, 'User not found. Please try registering again.')
                # Clear session data
                if 'pending_verification_user_id' in request.session:
                    del request.session['pending_verification_user_id']
                if 'pending_verification_identifier' in request.session:
                    del request.session['pending_verification_identifier']
                return render(request, 'register.html')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        login_identifier = request.POST.get('login_identifier')
        password = request.POST.get('password')

        try:
            # Try to find user by username, email, or phone number
            if is_email(login_identifier):
                user = User.objects.get(email=login_identifier)
            elif is_phone_number(login_identifier):
                profile = UserProfile.objects.get(phone_number=login_identifier)
                user = profile.user
            else:
                user = User.objects.get(username=login_identifier)

            if user.check_password(password):
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid password')

        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, 'User not found')

    return render(request, 'login.html')

def forgot_password_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')

        try:
            # Find user
            if is_email(identifier):
                user = User.objects.get(email=identifier)
                profile = user.userprofile
            else:
                profile = UserProfile.objects.get(phone_number=identifier)
                user = profile.user

            # If OTP is not provided, send it
            if not otp:
                new_otp = profile.generate_otp()
                send_otp_to_console(identifier, new_otp)
                messages.success(request, 'OTP sent! Check console (Development mode)')
                return render(request, 'forgot_password.html', {
                    'show_otp': True, 
                    'identifier': identifier
                })

            # If new password is not provided but OTP is, verify OTP
            elif not new_password:
                if profile.verify_otp(otp):
                    return render(request, 'forgot_password.html', {
                        'show_password': True,
                        'identifier': identifier,
                        'otp': otp
                    })
                else:
                    messages.error(request, 'Invalid or expired OTP')
                    return render(request, 'forgot_password.html', {
                        'show_otp': True,
                        'identifier': identifier
                    })

            # If both OTP and new password are provided
            else:
                if profile.verify_otp(otp):
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, 'Password updated successfully!')
                    return redirect('login')
                else:
                    messages.error(request, 'Invalid or expired OTP')

        except (User.DoesNotExist, UserProfile.DoesNotExist):
            messages.error(request, 'User not found')

    return render(request, 'forgot_password.html')

@login_required(login_url='login')
def home_view(request):
    return render(request, 'home.html')

def is_superuser(user):
    return user.is_superuser

@user_passes_test(is_superuser)
def delete_user(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, "You don't have permission to delete users")
        return redirect('home')
    
    # Add confirmation step for user deletion
    if request.method == 'POST':
        try:
            user = User.objects.get(id=user_id)
            # Log superuser actions for accountability
            if request.user.is_superuser:
                print(f"Superuser {request.user.username} deleted user {user_id}")
            user.delete()
            messages.success(request, "User deleted successfully")
        except User.DoesNotExist:
            messages.error(request, "User not found")
        return redirect('admin:auth_user_changelist')
    return render(request, 'confirm_delete.html', {'user_id': user_id})

@login_required
def add_to_cart(request, product_name, price):
    # Get or create the cart for the logged-in user
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Check if the item already exists in the cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product_name=product_name, price=price
    )

    if not created:
        # If the item already exists, increase the quantity
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

@login_required
def view_cart(request):
    # Get the cart for the logged-in user
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartitem_set.all()
    total_price = cart.total_price()

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })