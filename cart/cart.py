from decimal import Decimal
from django.conf import settings
from products.models import Product

class Cart:
    """
    A base Cart class, providing some default behaviors that
    can be inherited or overridden, as necessary.
    """
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        
    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'name': product.name,
                'type': product.type,
                'price': str(product.price),
                'description': product.description,
                'image': product.image.url if product.image else '',
                'quantity': 0,
                'discount': product.discount if hasattr(product, 'discount') else None,
            }
            
            # Calculate discounted price if discount exists
            if hasattr(product, 'discount') and product.discount:
                original_price = Decimal(product.price)
                discount_amount = original_price * (Decimal(product.discount) / Decimal('100'))
                discounted_price = original_price - discount_amount
                self.cart[product_id]['discounted_price'] = str(discounted_price.quantize(Decimal('0.01')))
                
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()
        
    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True
        
    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
            
    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        product_ids = self.cart.keys()
        # get the product objects and add them to the cart
        for product_id in product_ids:
            self.cart[product_id]['id'] = product_id
            
        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            # Use discounted price if available
            if 'discounted_price' in item:
                item['discounted_price'] = Decimal(item['discounted_price'])
                item['total_price'] = item['discounted_price'] * item['quantity']
            else:
                item['total_price'] = item['price'] * item['quantity']
            yield item
            
    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())
        
    def get_total_price(self):
        total = Decimal('0.0')
        for item in self.cart.values():
            price = Decimal(item['discounted_price']) if 'discounted_price' in item else Decimal(item['price'])
            total += price * item['quantity']
        return total
    
    def get_tax(self):
        """
        Calculate the tax amount (14% of total price)
        """
        total = self.get_total_price()
        tax = total * Decimal('0.14')
        return tax.quantize(Decimal('0.01'))
    
    def get_total_with_tax(self):
        """
        Calculate the total price including tax and shipping
        """
        total = self.get_total_price()
        tax = self.get_tax()
        shipping = Decimal('50.00')
        return total + tax + shipping
        
    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save() 