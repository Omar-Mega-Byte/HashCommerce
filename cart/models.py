from decimal import Decimal
import uuid

from django.db import models
from django.conf import settings

from products.models import Product
from utils.models import EncryptedTextFieldMixin



class Transaction(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('cash_on_delivery', 'Cash on Delivery'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    shipping_address = models.TextField(blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Transaction {self.id}"
    
    def get_total(self):
        return self.total_amount + self.tax_amount + self.shipping_amount


class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, related_name='items', on_delete=models.CASCADE)
    product_id = models.IntegerField()
    product_name = models.CharField(max_length=255)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_discount = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"
    
    @property
    def total_price(self):
        if self.product_discount:
            discount_decimal = Decimal(str(self.product_discount)) / Decimal('100')
            discounted_price = self.product_price * (Decimal('1.0') - discount_decimal)
            return discounted_price * Decimal(str(self.quantity))
        return self.product_price * Decimal(str(self.quantity))


class SecurePaymentInfo(models.Model, EncryptedTextFieldMixin):
    """
    Secure storage for sensitive payment information using AES encryption.
    
    This model uses the EncryptedTextFieldMixin to securely store
    credit card details and other payment information with AES encryption.
    """
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name='secure_payment')
    card_holder_name = models.CharField(max_length=255, blank=True, null=True)
    last_four_digits = models.CharField(max_length=4, blank=True, null=True)
    
 
    encrypted_data_cc_number = models.TextField(blank=True, null=True)
    encryption_salt_cc_number = models.TextField(blank=True, null=True)
    encrypted_data_cc_expiry = models.TextField(blank=True, null=True)
    encryption_salt_cc_expiry = models.TextField(blank=True, null=True)
    encrypted_data_cc_cvv = models.TextField(blank=True, null=True)
    encryption_salt_cc_cvv = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def set_card_number(self, value):
        """Set the encrypted credit card number."""
        if value:
            # Store last 4 digits unencrypted for reference
            self.last_four_digits = value[-4:] if len(value) >= 4 else value
            # Store full number encrypted
            self.set_encrypted_value(value, field_name='cc_number')
        
    def get_card_number(self):
        """Get the decrypted credit card number."""
        return self.get_encrypted_value(field_name='cc_number')
        
    def set_card_expiry(self, value):
        """Set the encrypted card expiry date."""
        self.set_encrypted_value(value, field_name='cc_expiry')
        
    def get_card_expiry(self):
        """Get the decrypted card expiry date."""
        return self.get_encrypted_value(field_name='cc_expiry')
        
    def set_card_cvv(self, value):
        """Set the encrypted card CVV/security code."""
        self.set_encrypted_value(value, field_name='cc_cvv')
        
    def get_card_cvv(self):
        """Get the decrypted card CVV/security code."""
        return self.get_encrypted_value(field_name='cc_cvv')
    
    def __str__(self):
        if self.last_four_digits:
            return f"Payment info (**** {self.last_four_digits})"
        return f"Payment info for transaction" 