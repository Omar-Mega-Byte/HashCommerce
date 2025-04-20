from django.contrib import admin
from .models import Transaction, TransactionItem

class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ('product_id', 'product_name', 'product_price', 'product_discount', 'quantity', 'total_price')
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'transaction_date', 'total_amount', 'payment_status', 'payment_method')
    list_filter = ('payment_status', 'payment_method', 'transaction_date')
    search_fields = ('id', 'user__username', 'user__email')
    date_hierarchy = 'transaction_date'
    readonly_fields = ('id', 'transaction_date')
    inlines = [TransactionItemInline]
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('id', 'user', 'transaction_date', 'payment_status', 'payment_method')
        }),
        ('Financial Details', {
            'fields': ('total_amount', 'tax_amount', 'shipping_amount')
        }),
        ('Address Information', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    ) 