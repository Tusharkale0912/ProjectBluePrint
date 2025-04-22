import re

def send_otp_to_console(identifier, otp):
    """Development version - prints OTP to console"""
    print("\n------------------------")
    print(f"Sending OTP: {otp} to: {identifier}")
    print("------------------------\n")
    return True

def is_email(value):
    """Check if value is an email"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, value) is not None

def is_phone_number(value):
    """Check if value is a phone number"""
    phone_regex = r'^\+?1?\d{9,15}$'
    return re.match(phone_regex, str(value)) is not None 