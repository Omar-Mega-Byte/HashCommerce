from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import View
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from .forms import RegisterForm, LoginForm
from .models import User

# Web views
def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('dashboard')
        messages.error(request, 'Invalid form submission.')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            # First check if user exists
            try:
                user = User.objects.get(email=email)
                # Check if account is active
                if not user.is_active:
                    messages.error(request, 'Your account has been deactivated. Please contact admin for assistance.')
                    return render(request, 'accounts/login.html', {'form': form})
                
                # Try to authenticate
                user = authenticate(request, email=email, password=password)
                if user:
                    login(request, user)
                    messages.success(request, 'Login successful.')
                    
                    # Check if there's a pending cart item
                    pending_product_id = request.session.get('pending_cart_item')
                    if pending_product_id:
                        # Remove the pending item from session
                        del request.session['pending_cart_item']
                        # Redirect to the product detail page
                        return redirect('products:detail', pk=pending_product_id)
                    
                    # Normal login flow
                    if user.is_admin:
                        return redirect('admin_panel:dashboard')
                    return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid password.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def password_reset_request_view(request):
    # For now, just render a simple template
    # This would typically involve sending an email with password reset link
    messages.info(request, 'Password reset functionality will be implemented soon.')
    return render(request, 'accounts/password_reset_request.html')

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'You have been logged out.')
    else:
        # If it's a GET request, show a confirmation page
        return render(request, 'accounts/logout_confirm.html')
    return redirect('login')

@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')

# API views for JWT authentication
class RegisterAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        form = RegisterForm(request.data)
        if form.is_valid():
            user = form.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {'email': user.email, 'name': user.get_full_name(), 'type': user.type}
            }, status=status.HTTP_201_CREATED)
        
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST) 