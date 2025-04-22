"""
Demo script showing how to use the cryptography utilities.
"""

from utils.crypto import encrypt_text, decrypt_text


def demo_encryption():
    """
    Simple demonstration of encryption and decryption functionality.
    """
    # Test data
    sensitive_data = "Very sensitive customer data: SSN 123-45-6789"
    print(f"Original text: {sensitive_data}")
    
    # Encrypt the data
    print("\nEncrypting...")
    encrypted_result = encrypt_text(sensitive_data)
    encrypted_data = encrypted_result['encrypted_data']
    salt = encrypted_result['salt']
    
    print(f"Encrypted data: {encrypted_data}")
    print(f"Salt: {salt}")
    
    # Decrypt the data
    print("\nDecrypting...")
    decrypted_data = decrypt_text(encrypted_data, salt)
    print(f"Decrypted text: {decrypted_data}")
    
    # Verify the decryption worked correctly
    print(f"\nDecryption successful: {decrypted_data == sensitive_data}")
    
    # Example with custom encryption key
    print("\n--- Using Custom Key ---")
    custom_key = "my-super-secret-password"
    
    encrypted_result = encrypt_text(sensitive_data, key=custom_key)
    encrypted_data = encrypted_result['encrypted_data']
    salt = encrypted_result['salt']
    
    print(f"Encrypted data with custom key: {encrypted_data}")
    
    decrypted_data = decrypt_text(encrypted_data, salt, key=custom_key)
    print(f"Decrypted text with custom key: {decrypted_data}")


if __name__ == "__main__":
    demo_encryption() 