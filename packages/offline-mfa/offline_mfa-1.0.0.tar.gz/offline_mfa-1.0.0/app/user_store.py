import base64
import os
import re
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from mysql.connector import pooling
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "totp_db"
}

# Initialize Database Connection Pooling
db_pool = pooling.MySQLConnectionPool(
    pool_name="mypool",
    pool_size=5,
    **DB_CONFIG
)

# Read encryption key
key_env = os.getenv("ENCRYPTION_KEY")
if key_env:
    SECRET_KEY = base64.b64decode(key_env)  # Decode from Base64
    if len(SECRET_KEY) != 32:
        raise ValueError("Invalid ENCRYPTION_KEY: Must be 32 bytes after decoding.")
else:
    raise ValueError("Missing ENCRYPTION_KEY in .env file!")

# AES-GCM Encryption Functions
def encrypt_data(data):
    """Encrypt data using AES-GCM."""
    nonce = os.urandom(12)
    aesgcm = AESGCM(SECRET_KEY)
    encrypted_data = aesgcm.encrypt(nonce, data.encode(), None)
    return base64.urlsafe_b64encode(nonce + encrypted_data).decode()

def decrypt_data(encrypted_data):
    """Decrypt AES-GCM encrypted data."""
    try:
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data)
        nonce, ciphertext = encrypted_bytes[:12], encrypted_bytes[12:]
        aesgcm = AESGCM(SECRET_KEY)
        return aesgcm.decrypt(nonce, ciphertext, None).decode()
    except Exception as e:
        print(f"Decryption failed: {e}")
        return None

def get_db_connection():
    """Get a database connection from the pool."""
    try:
        return db_pool.get_connection()
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def is_valid_username(username):
    """Ensure username contains only alphanumeric characters, underscores, hyphens, and dots."""
    return bool(re.match(r"^[a-zA-Z0-9_.-]+$", username))

def hash_username(username):
    """Hash the username using SHA-256 before storing it in DB."""
    return hashlib.sha256(username.encode()).hexdigest()

def get_user_from_db(username):
    """Fetch user data using hashed username."""
    if not is_valid_username(username):
        print("Invalid username format!")
        return None

    hashed_username = hash_username(username)
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT secret_key FROM users WHERE username = %s"
        cursor.execute(query, (hashed_username,))
        result = cursor.fetchone()
        return result if result else None
    except Exception as e:
        print(f"Database error: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def save_user_to_db(username, secret):
    """Save user data using hashed username in MySQL."""
    if not is_valid_username(username):
        print("Invalid username format! Not saving to DB.")
        return False

    hashed_username = hash_username(username)
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO users (username, secret_key) 
        VALUES (%s, %s) 
        ON DUPLICATE KEY UPDATE secret_key = VALUES(secret_key)
        """
        cursor.execute(query, (hashed_username, secret))
        conn.commit()
        print(f"User {username} saved securely to MySQL.")
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def delete_user_from_db(username):
    """Delete a user from the database."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            query = "DELETE FROM users WHERE username = %s"
            cursor.execute(query, (hash_username(username),))
            conn.commit()
            print(f"User {username} deleted from database.")
        except Exception as e:
            print(f"Database error: {e}")
        finally:
            cursor.close()
            conn.close()
