from app.auth import register_user, generate_totp_token, verify_totp_token
from app.user_store import get_user_from_db

def main():
    print("=== Offline MFA Demo ===")

    username = input("Enter username: ")

    # Check if the user already exists in the database
    user = get_user_from_db(username)

    if user:
        print(f"User {username} already exists. Using stored secret for OTP generation...")
    else:
        print(f"User {username} does not exist. Registering...")
        secret = register_user(username)
        if secret:    
            print(f"User {username} registered successfully. Save this TOTP secret: {secret}")
        else:
            print("Error during registration. Exiting.")
            return

    # Generate a TOTP token
    print("\nGenerating a TOTP token...")
    try:
        token, time_left = generate_totp_token(username)
        # print(f"TOTP Token: {token} (Expires in {time_left} seconds)")
    except ValueError as e:
        print(f"Error: {e}")
        return

    # Verify the TOTP token
    user_token = input("\nEnter the TOTP token for verification: ")
    if verify_totp_token(username, user_token):
        print("TOTP verification successful!")
    else:
        print("Authentication failed.")

if __name__ == "__main__":
    main()
