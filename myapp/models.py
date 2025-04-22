from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    def generate_otp(self):
        from random import randint
        self.otp = str(randint(100000, 999999))
        self.otp_created_at = timezone.now()
        self.save()
        return self.otp

    def verify_otp(self, entered_otp):
        if not self.otp or not self.otp_created_at:
            return False
        
        # Check if OTP is expired (5 minutes)
        if timezone.now() > self.otp_created_at + timezone.timedelta(minutes=5):
            return False
        
        if str(self.otp) == str(entered_otp):
            self.otp = None
            self.otp_created_at = None
            self.save()
            return True
        return False

    def __str__(self):
        return f"{self.user.username}'s profile"


class Creator(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    age = models.IntegerField()
    number = models.IntegerField()

