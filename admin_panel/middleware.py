from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class AdminAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin-page/'):
            # Check if user is authenticated and is an admin
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to access the admin panel.")
                return redirect(reverse('login') + '?next=' + request.path)
            
            if not request.user.is_staff and not request.user.is_admin:
                messages.error(request, "You don't have permission to access the admin panel.")
                return redirect('products:index')
        
        response = self.get_response(request)
        return response 