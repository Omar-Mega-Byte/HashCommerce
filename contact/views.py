from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactUs
from django.views.decorators.http import require_http_methods
from .forms import ContactForm

@require_http_methods(["GET", "POST"])
def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        contact = ContactUs(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        contact.save()
        
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact:contact_success')
    
    return render(request, 'contact/contact_form.html')

def contact_success_view(request):
    return render(request, 'contact/contact_success.html')

def contact_us(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent. We will get back to you soon!')
            return redirect('contact:contact_us')
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact_form.html', {'form': form}) 