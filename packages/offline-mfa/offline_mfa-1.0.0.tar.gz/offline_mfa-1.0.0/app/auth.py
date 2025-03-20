import pyotp
import time
from datetime import datetime
from app.user_store import save_user_to_db, get_user_from_db, encrypt_data, decrypt_data

# Dictionary to track failed OTP attempts per user
failed_attempts = {}

def rate_limit(username):
    """Limit OTP verification attempts to prevent brute-force attacks."""
    if username in failed_attempts:
        if failed_attempts[username]["attempts"] >= 5:
            last_attempt_time = failed_attempts[username]["time"]
            if time.time() - last_attempt_time < 60:  # 1-minute cooldown
                print("Too many attempts. Try again later.")
                return False
            else:
                failed_attempts[username] = {"attempts": 1, "time": time.time()}
        else:
            failed_attempts[username]["attempts"] += 1
    else:
        failed_attempts[username] = {"attempts": 1, "time": time.time()}

    return True

def generate_totp_secret():
    """Generate a new TOTP secret."""
    return pyotp.random_base32()

def register_user(username):
    """Register a new user or return existing user's secret."""
    existing_user = get_user_from_db(username)

    if existing_user:
        decrypted_secret = decrypt_data(existing_user["secret_key"])
        print(f"User {username} already exists. Reusing stored secret.")
        return decrypted_secret  # Return existing decrypted secret
    
    secret = generate_totp_secret()
    encrypted_secret = encrypt_data(secret)
    
    # Save new user with encrypted secret
    save_user_to_db(username, encrypted_secret)
    
    # print(f"User {username} registered successfully. Save this TOTP secret: {secret}")
    return secret

def generate_totp_token(username):
    """Generate a TOTP token for the user."""
    user = get_user_from_db(username)
    if not user or not user["secret_key"]:
        raise ValueError("User not found or Secret is None")

    decrypted_secret = decrypt_data(user["secret_key"])
    totp = pyotp.TOTP(decrypted_secret)
    token = totp.now()
    time_left = 30 - (int(datetime.now().timestamp()) % 30)

    return token, time_left

def verify_totp_token(username, token):
    """Verify the TOTP token with rate limiting and three attempts."""
    if not rate_limit(username):
        return False  # Rate limit exceeded

    user = get_user_from_db(username)
    if not user:
        print("User not found.")
        return False

    decrypted_secret = decrypt_data(user["secret_key"])
    totp = pyotp.TOTP(decrypted_secret)
    
    attempts = 3  # Allow three attempts
    
    while attempts > 0:
        if totp.verify(token, valid_window=1):  # Allow slight time drift
            # print("TOTP verification successful!")
            return True
        else:
            attempts -= 1
            if attempts > 0:
                print(f"Invalid TOTP token. You have {attempts} attempts remaining.")
                token = input("Enter TOTP again: ")  # Prompt user for new input
            else:
                print("Invalid TOTP token.")
                return False

