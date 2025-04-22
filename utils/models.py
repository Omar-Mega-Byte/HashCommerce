"""
Utility models and model fields for the Django ecommerce application.
"""

from django.db import models
from .crypto import encrypt_text, decrypt_text


class EncryptedTextFieldMixin:
    """
    A model mixin that provides encrypted text storage.
    
    This is not a Django model but a mixin to be used with models
    that need encrypted field storage.
    """
    
    def set_encrypted_value(self, value, field_name=None, key=None):
        """
        Encrypt a value and store the encrypted data and salt.
        
        Args:
            value: The value to encrypt
            field_name: Optional field name suffix if storing multiple encrypted values
            key: Optional encryption key
        """
        if value is None:
            return
            
        encrypted = encrypt_text(value, key=key)
        
        suffix = f"_{field_name}" if field_name else ""
        setattr(self, f"encrypted_data{suffix}", encrypted['encrypted_data'])
        setattr(self, f"encryption_salt{suffix}", encrypted['salt'])
    
    def get_encrypted_value(self, field_name=None, key=None):
        """
        Decrypt and return the stored encrypted value.
        
        Args:
            field_name: Optional field name suffix if storing multiple encrypted values
            key: Optional encryption key
            
        Returns:
            The decrypted value or None if not set
        """
        suffix = f"_{field_name}" if field_name else ""
        encrypted_data = getattr(self, f"encrypted_data{suffix}", None)
        encryption_salt = getattr(self, f"encryption_salt{suffix}", None)
        
        if not encrypted_data or not encryption_salt:
            return None
            
        try:
            return decrypt_text(encrypted_data, encryption_salt, key=key)
        except Exception:
            return None 