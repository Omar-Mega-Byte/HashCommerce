"""
Cryptography utilities for secure data encryption and decryption.

This module provides functions for AES encryption and decryption using
Fernet (symmetric encryption), which is built on AES in CBC mode with
PKCS7 padding and HMAC using SHA256 for authentication.
"""

import base64
import os
from typing import Optional, Tuple, Union
from django.conf import settings
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class Crypto:
    """
    Utility class for encryption and decryption operations.
    """
    
    @staticmethod
    def generate_key(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Generate a Fernet key from a password.
        
        Args:
            password: The password to use for key derivation
            salt: Optional salt for key derivation, generated if not provided
            
        Returns:
            Tuple containing (key, salt)
        """
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    @staticmethod
    def encrypt(data: Union[str, bytes], key: Optional[str] = None) -> dict:
        """
        Encrypt data using Fernet symmetric encryption (AES-128 in CBC mode).
        
        Args:
            data: The data to encrypt (string or bytes)
            key: Optional encryption key, defaults to Django's SECRET_KEY
            
        Returns:
            Dictionary containing encrypted data and salt
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        password = key or settings.SECRET_KEY
        key, salt = Crypto.generate_key(password)
        
        f = Fernet(key)
        encrypted_data = f.encrypt(data)
        
        return {
            'encrypted_data': base64.urlsafe_b64encode(encrypted_data).decode('ascii'),
            'salt': base64.urlsafe_b64encode(salt).decode('ascii')
        }
    
    @staticmethod
    def decrypt(encrypted_data: str, salt: str, key: Optional[str] = None) -> bytes:
        """
        Decrypt Fernet-encrypted data.
        
        Args:
            encrypted_data: The encrypted data as a base64 string
            salt: The salt used for encryption as a base64 string
            key: Optional encryption key, defaults to Django's SECRET_KEY
            
        Returns:
            Decrypted data as bytes
        """
        encrypted_data_bytes = base64.urlsafe_b64decode(encrypted_data.encode('ascii'))
        salt_bytes = base64.urlsafe_b64decode(salt.encode('ascii'))
        
        password = key or settings.SECRET_KEY
        key, _ = Crypto.generate_key(password, salt_bytes)
        
        f = Fernet(key)
        return f.decrypt(encrypted_data_bytes)


def encrypt_text(text: str, key: Optional[str] = None) -> dict:
    """
    Convenience function to encrypt text data.
    
    Args:
        text: Text to encrypt
        key: Optional encryption key
        
    Returns:
        Dictionary with encrypted data and salt
    """
    return Crypto.encrypt(text, key)


def decrypt_text(encrypted_data: str, salt: str, key: Optional[str] = None) -> str:
    """
    Convenience function to decrypt text data.
    
    Args:
        encrypted_data: The encrypted data as a base64 string
        salt: The salt used during encryption
        key: Optional encryption key
        
    Returns:
        Decrypted text as string
    """
    decrypted_bytes = Crypto.decrypt(encrypted_data, salt, key)
    return decrypted_bytes.decode('utf-8') 