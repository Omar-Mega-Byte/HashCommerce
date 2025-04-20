from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Web routes
    path('', views.PostListView.as_view(), name='list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='detail'),
    
    # API routes can be added here later
] 