from cryptography.fernet import Fernet
from django.conf import settings
import base64
import os

# Generate a secure encryption key
def generate_encryption_key():
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key().decode()

def get_encryption_key():
    """Get the encryption key from settings or generate a new one."""
    key = getattr(settings, 'ENCRYPTION_KEY', None)
    if not key:
        # For development, we can generate a key, but in production this should be set
        key = generate_encryption_key()
        print(f"⚠️  Generated new encryption key: {key[:20]}... (For development only)")
    return key

def get_fernet_instance():
    """Get a Fernet instance with the configured key."""
    return Fernet(get_encryption_key().encode())

def encrypt_data(data):
    """Encrypt sensitive data."""
    if data is None or data == "":
        return None
        
    fernet = get_fernet_instance()
    encrypted_data = fernet.encrypt(data.encode())
    return base64.b64encode(encrypted_data).decode()

def decrypt_data(encrypted_data):
    """Decrypt sensitive data."""
    if encrypted_data is None or encrypted_data == "":
        return None
        
    try:
        fernet = get_fernet_instance()
        decoded_data = base64.b64decode(encrypted_data.encode())
        return fernet.decrypt(decoded_data).decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return None

class EncryptedField:
    """Descriptor for encrypted model fields."""
    
    def __init__(self, field_name):
        self.field_name = field_name
        
    def __get__(self, instance, owner):
        if instance is None:
            return self
        encrypted_value = instance.__dict__.get(self.field_name)
        return decrypt_data(encrypted_value)
        
    def __set__(self, instance, value):
        instance.__dict__[self.field_name] = encrypt_data(value) if value else None