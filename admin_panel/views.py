from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from products.models import Product
from accounts.models import User
from contact.models import ContactUs
from .forms import ProductForm, UserEditForm

# Create your views here.

@login_required
def admin_dashboard(request):
    # Get some statistics for the dashboard
    total_products = Product.objects.count()
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    inactive_users = User.objects.filter(is_active=False).count()
    total_contacts = ContactUs.objects.count()
    unread_contacts = ContactUs.objects.filter(is_read=False).count()
    
    context = {
        'total_products': total_products,
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'total_contacts': total_contacts,
        'unread_contacts': unread_contacts,
    }
    return render(request, 'admin_panel/dashboard.html', context)

@login_required
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/product_list.html', {'products': products})

@login_required
def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully.')
            return redirect('admin_panel:product_list')
    else:
        form = ProductForm()
    
    return render(request, 'admin_panel/product_form.html', {
        'form': form,
        'title': 'Add New Product',
        'submit_text': 'Add Product'
    })

@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('admin_panel:product_list')
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'admin_panel/product_form.html', {
        'form': form,
        'product': product,
        'title': 'Edit Product',
        'submit_text': 'Update Product'
    })

@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('admin_panel:product_list')
    
    return render(request, 'admin_panel/product_delete.html', {'product': product})

@login_required
def user_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin_panel/user_list.html', {'users': users})

@login_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    return render(request, 'admin_panel/user_detail.html', {'user_obj': user})

@login_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User updated successfully.')
            return redirect('admin_panel:user_list')
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'admin_panel/user_form.html', {
        'form': form,
        'user_obj': user,
        'title': 'Edit User',
        'submit_text': 'Update User'
    })

@login_required
def contact_list(request):
    contacts = ContactUs.objects.all().order_by('-created_at')
    return render(request, 'admin_panel/contact_list.html', {'contacts': contacts})

@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(ContactUs, pk=pk)
    
    if request.method == 'POST' and 'mark_as_read' in request.POST:
        contact.is_read = True
        contact.save()
        messages.success(request, 'Message marked as read.')
        return redirect('admin_panel:contact_detail', pk=contact.id)
    
    # If it's not already read, mark it as read automatically when viewed
    if not contact.is_read:
        contact.is_read = True
        contact.save()
    
    return render(request, 'admin_panel/contact_detail.html', {'contact': contact})

@login_required
def contact_delete(request, pk):
    contact = get_object_or_404(ContactUs, pk=pk)
    
    if request.method == 'POST':
        contact.delete()
        messages.success(request, 'Contact message deleted successfully.')
        return redirect('admin_panel:contact_list')
    
    return render(request, 'admin_panel/contact_delete.html', {'contact': contact})
