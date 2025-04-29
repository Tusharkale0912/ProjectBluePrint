from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import hashlib
import random
import string


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    otp_hash = models.CharField(max_length=128, null=True, blank=True)  # Store hashed OTP instead of plain text
    otp_created_at = models.DateTimeField(null=True, blank=True)
    otp_attempts = models.IntegerField(default=0)  # Track failed attempts for rate limiting
    last_otp_attempt = models.DateTimeField(null=True, blank=True)  # Track when the last attempt was made

    def generate_otp(self):
        """Generate a secure OTP and store its hash"""
        # Check rate limiting - only allow 3 OTP generations per hour
        if self.otp_created_at and self.otp_attempts >= 3:
            time_since_last = timezone.now() - self.otp_created_at
            if time_since_last.total_seconds() < 3600:  # 1 hour in seconds
                return None  # Rate limit exceeded
        
        # Generate a random 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        
        # Hash the OTP before storing
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        
        # Store the hash and reset attempts
        self.otp_hash = otp_hash
        self.otp_created_at = timezone.now()
        self.otp_attempts = 0
        self.save()
        
        return otp

    def verify_otp(self, entered_otp):
        """Verify the entered OTP against the stored hash"""
        if not self.otp_hash or not self.otp_created_at:
            return False
        
        # Check if OTP is expired (10 minutes instead of 5)
        if timezone.now() > self.otp_created_at + timezone.timedelta(minutes=10):
            return False
        
        # Remove the 1-minute cooldown between attempts
        # This was causing issues with verification
        
        # Update last attempt time
        self.last_otp_attempt = timezone.now()
        self.otp_attempts += 1
        
        # Hash the entered OTP and compare with stored hash
        entered_hash = hashlib.sha256(str(entered_otp).encode()).hexdigest()
        
        if self.otp_hash == entered_hash:
            # Clear OTP data after successful verification
            self.otp_hash = None
            self.otp_created_at = None
            self.otp_attempts = 0
            self.last_otp_attempt = None
            self.save()
            return True
        
        # Save the attempt count even if verification fails
        self.save()
        return False

    def __str__(self):
        return f"{self.user.username}'s profile"


class Creator(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    number = models.IntegerField()

