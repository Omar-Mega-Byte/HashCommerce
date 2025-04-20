from django import forms
from products.models import Product
from accounts.models import User
from contact.models import ContactUs

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'type', 'price', 'description', 'image', 'discount']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Add custom widgets for specific fields
        self.fields['description'].widget = forms.Textarea(attrs={'rows': 4, 'class': 'form-control'})
        self.fields['price'].widget.attrs.update({'min': 0})
        self.fields['discount'].widget.attrs.update({'min': 0})

class UserEditForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirm_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'type', 'is_active', 'is_staff']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
            
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match')
            
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        
        if password:
            user.set_password(password)
            
        if commit:
            user.save()
            
        return user 