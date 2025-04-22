from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile
from .utils import send_otp_to_console, is_email, is_phone_number
import re
import random

def is_email(value):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, value) is not None

def is_phone_number(value):
    phone_regex = r'^\+?1?\d{9,15}$'
    return re.match(phone_regex, value) is not None

def register_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        otp = request.POST.get('otp')

        # If OTP is not provided, this is the first step
        if not otp:
            # Check if user already exists
            if User.objects.filter(email=identifier).exists() or \
               UserProfile.objects.filter(phone_number=identifier).exists():
                messages.error(request, 'User already exists')
                return render(request, 'register.html')

            # Create user first
            if is_email(identifier):
                user = User.objects.create_user(
                    username=identifier.split('@')[0],
                    email=identifier,
                    password=password
                )
                profile = UserProfile.objects.create(
                    user=user,
                    is_email_verified=False
                )
            else:
                user = User.objects.create_user(
                    username=f"user_{identifier}",
                    password=password
                )
                profile = UserProfile.objects.create(
                    user=user,
                    phone_number=identifier,
                    is_phone_verified=False
                )

            # Generate and send OTP
            new_otp = profile.generate_otp()
            send_otp_to_console(identifier, new_otp)
            
            # Store user ID in session for verification
            request.session['pending_verification_user_id'] = user.id
            
            messages.success(request, 'OTP sent! Check console (Development mode)')
            return render(request, 'register.html', {'show_otp': True, 'identifier': identifier})

        else:
            # Verify OTP
            user_id = request.session.get('pending_verification_user_id')
            if not user_id:
                messages.error(request, 'Registration data not found')
                return render(request, 'register.html')

            try:
                user = User.objects.get(id=user_id)
                profile = user.userprofile

                if profile.verify_otp(otp):
                    # Mark verification as complete
                    if is_email(identifier):
                        profile.is_email_verified = True
                    else:
                        profile.is_phone_verified = True
                    profile.save()

                    del request.session['pending_verification_user_id']
                    login(request, user)
                    messages.success(request, 'Registration successful!')
                    return redirect('home')
                else:
                    messages.error(request, 'Invalid or expired OTP')
                    return render(request, 'register.html', {'show_otp': True, 'identifier': identifier})

            except (User.DoesNotExist, UserProfile.DoesNotExist):
                messages.error(request, 'User not found')
                return render(request, 'register.html')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')

        try:
            if is_email(identifier):
                user = User.objects.get(email=identifier)
            elif is_phone_number(identifier):
                profile = UserProfile.objects.get(phone_number=identifier)
                user = profile.user
            else:
                user = User.objects.get(username=identifier)

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
    
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        messages.success(request, "User deleted successfully")
    except User.DoesNotExist:
        messages.error(request, "User not found")
    
    return redirect('admin:auth_user_changelist')