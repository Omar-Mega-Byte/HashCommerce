from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Web routes
    path('', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('clear/', views.cart_clear, name='cart_clear'),
    
    # Web routes - Transactions
    path('transactions/', views.transaction_history, name='transaction_history'),
    path('transactions/<uuid:transaction_id>/', views.transaction_detail, name='transaction_detail'),
    
    # API routes
    path('api/cart/', views.CartAPIView.as_view(), name='api_cart'),
    path('api/cart/clear/', views.CartClearAPIView.as_view(), name='api_cart_clear'),
] 