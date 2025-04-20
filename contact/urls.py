from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    # Web routes
    path('', views.contact_us, name='contact_us'),
    path('success/', views.contact_success_view, name='contact_success'),
    
    # API routes can be added here later
] 