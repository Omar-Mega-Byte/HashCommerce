# Django E-Commerce

This is a Python (Django) version of an e-commerce platform with JWT authentication.

## Features

- Product catalog
- Shopping cart functionality
- User authentication with JWT
- Admin dashboard
- Blog posts
- Contact form

## Installation

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create a superuser: `python manage.py createsuperuser`
7. Run the development server: `python manage.py runserver`

## Project Structure

- `ecommerce/` - Main Django project
- `core/` - Core application for shared functionality
- `products/` - Product management app
- `cart/` - Shopping cart app
- `accounts/` - User authentication and management
- `blog/` - Blog post management
- `contact/` - Contact form functionality

## Authentication

This project uses JWT (JSON Web Tokens) for authentication. Tokens are provided upon login and must be included in the Authorization header for protected API endpoints. 