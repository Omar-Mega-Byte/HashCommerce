from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'products'

# API router
router = DefaultRouter()
router.register(r'api/products', views.ProductViewSet)

urlpatterns = [
    # Web routes
    path('', views.ProductListView.as_view(), name='index'),
    path('shop/', views.ShopView.as_view(), name='shop'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='detail'),
    
    # API routes
    path('', include(router.urls)),
] 