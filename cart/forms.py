from django import forms
from .models import Transaction, SecurePaymentInfo
import re


class PaymentForm(forms.Form):
    """
    Form for secure payment information processing.
    The sensitive data will be encrypted before being stored.
    """
    # Transaction info
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), 
        required=True
    )
    billing_address = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), 
        required=True
    )
    payment_method = forms.ChoiceField(
        choices=Transaction.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        required=False
    )
    
    # Credit card details (these will be encrypted)
    card_holder_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    card_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[0-9 ]*',
            'inputmode': 'numeric',
            'placeholder': 'XXXX XXXX XXXX XXXX',
            'autocomplete': 'cc-number',
            'maxlength': '19'  
        }),
        required=True
    )
    expiry_date = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'MM/YY',
            'autocomplete': 'cc-exp',
            'maxlength': '5'
        }),
        required=True
    )
    cvv = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[0-9]*',
            'inputmode': 'numeric',
            'maxlength': '4',
            'placeholder': 'CVV',
            'autocomplete': 'cc-csc'
        }),
        required=True
    )
    
    def clean_card_number(self):
        
        card_number = self.cleaned_data.get('card_number')

        card_number = card_number.replace(' ', '').replace('-', '')
        
        if not card_number.isdigit():
            raise forms.ValidationError("Card number should only contain digits.")
        
        card_type = self.detect_card_type(card_number)
        
        if card_type == 'amex' and len(card_number) != 15:
            raise forms.ValidationError("American Express cards must have 15 digits.")
        elif card_type in ['visa', 'mastercard', 'discover'] and len(card_number) != 16:
            raise forms.ValidationError(f"{card_type.title()} cards must have 16 digits.")
        elif not 13 <= len(card_number) <= 19:
            raise forms.ValidationError("Card number should be between 13 and 19 digits.")
            
        # Luhn algorithm check for card validity
        if not self.is_luhn_valid(card_number):
            raise forms.ValidationError("Invalid card number. Please check and try again.")
            
        return card_number
    
    def detect_card_type(self, card_number):
        """
        Detect the card type based on the card number prefix.
        Returns: 'visa', 'mastercard', 'amex', 'discover', or 'unknown'
        """
        if not card_number or not card_number.isdigit():
            return 'unknown'
            
        
        if card_number.startswith('4'):
            return 'visa'
            
        
        if card_number.startswith(('51', '52', '53', '54', '55')) or \
           (len(card_number) >= 4 and 2221 <= int(card_number[:4]) <= 2720):
            return 'mastercard'
            
    
        if card_number.startswith(('34', '37')):
            return 'amex'
            
        # Discover: Starts with 6011, 622126-622925, 644-649, or 65
        if card_number.startswith('6011') or \
           (len(card_number) >= 6 and 622126 <= int(card_number[:6]) <= 622925) or \
           card_number.startswith(('644', '645', '646', '647', '648', '649')) or \
           card_number.startswith('65'):
            return 'discover'
            
        return 'unknown'
    
    def is_luhn_valid(self, card_number):
        """
        Validate card number using the Luhn algorithm.
        More reliable implementation.
        """
        if not card_number or not card_number.isdigit():
            return False
            
        # Convert to list of integers
        digits = [int(d) for d in card_number]
        
        # Double every second digit from right to left
        for i in range(len(digits) - 2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
                
        # Sum all digits
        total = sum(digits)
        
        # Check if divisible by 10
        return total % 10 == 0
    
    def clean_expiry_date(self):
        """Validate the expiry date format and check for expired cards."""
        expiry_date = self.cleaned_data.get('expiry_date')
        
        # Check format MM/YY
        if not re.match(r'^(0[1-9]|1[0-2])/\d{2}$', expiry_date):
            raise forms.ValidationError("Expiry date should be in format MM/YY.")
            
        # Extract month and year
        month_str, year_str = expiry_date.split('/')
        month = int(month_str)
        year = int('20' + year_str)  # Convert to 4-digit year
        
        # Get current date for comparison
        from datetime import datetime
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        # Check if card has expired
        if (year < current_year) or (year == current_year and month < current_month):
            raise forms.ValidationError("This card has expired. Please use a valid card.")
        
        # Check if month is valid (1-12)
        if not 1 <= month <= 12:
            raise forms.ValidationError("Invalid month. Month should be between 01 and 12.")
            
        return expiry_date
    
    def clean_cvv(self):
        """Validate the CVV format."""
        cvv = self.cleaned_data.get('cvv')
        
        if not cvv.isdigit() or not 3 <= len(cvv) <= 4:
            raise forms.ValidationError("CVV should be 3 or 4 digits.")
            
        return cvv
    
    def save_payment_info(self, transaction):
        """
        Save payment information, encrypting sensitive data.
        
        Args:
            transaction: The Transaction model object to link payment to
        
        Returns:
            The SecurePaymentInfo instance with encrypted data
        """
        payment_info = SecurePaymentInfo(
            transaction=transaction,
            card_holder_name=self.cleaned_data.get('card_holder_name')
        )
        
        # Set the encrypted values
        payment_info.set_card_number(self.cleaned_data.get('card_number'))
        payment_info.set_card_expiry(self.cleaned_data.get('expiry_date'))
        payment_info.set_card_cvv(self.cleaned_data.get('cvv'))
        
        payment_info.save()
        return payment_info 