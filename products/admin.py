from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'price', 'discount', 'created_at')
    list_filter = ('type', 'created_at')
    search_fields = ('name', 'description', 'type')
    ordering = ('-created_at',) 