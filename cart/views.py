from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from products.models import Product
from .cart import Cart
from .forms import PaymentForm
from .models import Transaction, TransactionItem, SecurePaymentInfo

# Web views
@require_POST
def cart_add(request, product_id):
    if not request.user.is_authenticated:
        request.session['pending_cart_item'] = product_id
        messages.info(request, 'Please log in to add items to your cart.')
        return redirect('login')
    
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product=product)
    messages.success(request, 'Product added to cart!')
    return redirect('products:detail', pk=product_id)

@login_required
@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity, override_quantity=True)
    messages.success(request, 'Cart updated!')
    return redirect('cart:cart_detail')

@login_required
def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/index.html', {'cart': cart})

@login_required
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.success(request, 'Product removed from cart!')
    return redirect('cart:cart_detail')

@login_required
def checkout(request):
    """
    Handle checkout process with secure payment information.
    """
    cart = Cart(request)
    
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart:cart_detail')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Create the transaction
            transaction = Transaction.objects.create(
                user=request.user,
                total_amount=cart.get_total_price(),
                tax_amount=cart.get_tax(),
                shipping_amount=Decimal('50.00'),
                payment_method=form.cleaned_data['payment_method'],
                payment_status='completed',
                shipping_address=form.cleaned_data['shipping_address'],
                billing_address=form.cleaned_data['billing_address'],
                notes=form.cleaned_data['notes']
            )
            
            # Create transaction items
            for item in cart:
                TransactionItem.objects.create(
                    transaction=transaction,
                    product_id=item['id'],
                    product_name=item['name'],
                    product_price=item['price'],
                    product_discount=item.get('discount'),
                    quantity=item['quantity']
                )
            
            # Save payment info with encryption
            payment_info = form.save_payment_info(transaction)
            
            # Clear the cart
            cart.clear()
            
            messages.success(request, f'Your order has been placed! Transaction ID: {transaction.id}')
            return redirect('cart:transaction_detail', transaction_id=transaction.id)
    else:
        form = PaymentForm()
    
    return render(request, 'cart/checkout.html', {
        'form': form,
        'cart': cart
    })

@login_required
def cart_clear(request):
    cart = Cart(request)
    
    if len(cart) > 0:
        payment_method = request.POST.get('payment_method', 'cash_on_delivery')
        
        transaction = Transaction.objects.create(
            user=request.user,
            total_amount=cart.get_total_price(),
            tax_amount=cart.get_tax(),
            shipping_amount=Decimal('50.00'),
            payment_method=payment_method,
            payment_status='completed',
        )
        
        for item in cart:
            TransactionItem.objects.create(
                transaction=transaction,
                product_id=item['id'],
                product_name=item['name'],
                product_price=item['price'],
                product_discount=item.get('discount'),
                quantity=item['quantity']
            )
        
        cart.clear()
        messages.success(request, f'Your order has been placed! Transaction ID: {transaction.id}')
    else:
        messages.warning(request, 'Your cart is empty.')
    
    return redirect('cart:cart_detail')

@login_required
def transaction_history(request):
    transactions = Transaction.objects.filter(user=request.user).order_by('-transaction_date')
    return render(request, 'cart/transaction_history.html', {'transactions': transactions})

@login_required
def transaction_detail(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    # Try to get secure payment info if available
    try:
        payment_info = transaction.secure_payment
    except SecurePaymentInfo.DoesNotExist:
        payment_info = None
        
    return render(request, 'cart/transaction_detail.html', {
        'transaction': transaction,
        'payment_info': payment_info
    })

# API views
class CartAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        cart = Cart(request)
        return Response({
            'cart': list(cart),
            'total': cart.get_total_price(),
            'tax': cart.get_tax(),
            'total_with_tax': cart.get_total_with_tax()
        })
    
    def post(self, request):
        cart = Cart(request)
        try:
            product_id = request.data.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            cart.add(product=product)
            return Response({'status': 'Product added to cart'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    def delete(self, request):
        cart = Cart(request)
        try:
            product_id = request.data.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            cart.remove(product)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CartClearAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        cart = Cart(request)
        cart.clear()
        return Response({'status': 'Cart cleared'}, status=status.HTTP_200_OK) 