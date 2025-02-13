from django.db.models import Count
from django.shortcuts import render,redirect
from django.views import View
from .models import Product
from django.contrib import messages
from django.views.generic.edit import UpdateView
from .models import Contact,Customer,Cart
from .forms import CustomerRegistrationForm, CustomerProfileForm
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q

# Create your views here.
def home(request):
    return render(request, 'app/home.html')

def contact(request):
    return render(request, 'app/contact.html')

class CategoryView(View):
    def get(self, request,val):
        product = Product.objects.filter(category=val)
        title = Product.objects.filter(category=val).values('title')
        return render(request, 'app/category.html',locals())
    

class ProductDetail(View):
    def get(self, request,pk):
          product = Product.objects.get(pk=pk)
          return render(request, 'app/productdetail.html',locals())
    
import logging

logger = logging.getLogger(__name__)



def contact_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if name and email and message:
            Contact.objects.create(name=name, email=email, message=message)
            print("Message sent successfully")  # Debug print
            messages.success(request, "Your message has been sent successfully! ✅")
            return redirect("contact")
        else:
            print("Some fields are missing")  # Debug print
            messages.error(request, "All fields are required!")

    return render(request, "app/contact.html")

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/registration.html', locals())
    def post(self, request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Congratulations! User Register Successfully")
        else:
            messages.warning(request, "Registration failed")
        return render(request, 'app/registration.html',locals())



from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from .forms import CustomerProfileForm
from .models import Customer

class ProfileView(View):
    def get(self, request):  
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form': form})

    def post(self, request):
        form = CustomerProfileForm(request.POST) 
        if form.is_valid():
            user = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            mobile = form.cleaned_data['mobile']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']  # ✅ Fix applied here

            reg = Customer(
                user=user,
                name=name,
                locality=locality,
                mobile=mobile,
                city=city,
                state=state,
                zipcode=zipcode
            )
            reg.save()
            messages.success(request, "Profile updated successfully")
            return redirect('profile')  # ✅ Redirect after saving
        else:
            messages.warning(request, "Profile update failed")  

        return render(request, 'app/profile.html', {'form': form})  # ✅ Pass dictionary, not `locals()`

def address(request):
    add = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', locals())

class UpdateAddressView(View):
    def get(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(instance=add)  # Pass instance
        return render(request, 'app/updateaddress.html', {'form': form, 'add': add})

    def post(self, request, pk):
        add = Customer.objects.get(pk=pk)
        form = CustomerProfileForm(request.POST, instance=add)  # Update existing instance
        if form.is_valid():
            form.save()  # Save form directly
            messages.success(request, "Address updated successfully")
            return redirect('address')  # Redirect to address page after success
        else:
            messages.warning(request, "Address update failed")
        return render(request, 'app/updateaddress.html', {'form': form, 'add': add})  # Reload with errors

def add_to_cart(request):
    user=request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    Cart(user=user, product=product).save()
    return redirect('/cart')

def show_cart(request):
    user=request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    for p in cart :
        value = p.quantity * p.product.price
        amount = amount + value
    totalamount = amount + 40 
    return render(request, 'app/addtocart.html', locals())

from django.shortcuts import render
from django.views import View
from .models import Customer, Cart

class Checkout(View):
    def get(self, request):
        user = request.user
        addresses = Customer.objects.filter(user=user)  # Fetch all addresses
        cart_items = Cart.objects.filter(user=user)  # Fetch cart items
        totalamount = sum(item.quantity * item.product.price for item in cart_items) + 40  # Total price + shipping
        
        # Debugging ke liye print karo
        print("Addresses:", addresses)  
        
        return render(request, 'app/checkout.html', {
            'addresses': addresses,
            'cart_items': cart_items,
            'totalamount': totalamount
        })

from django.http import JsonResponse
from .models import Cart

def plus_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get('prod_id')
        if not prod_id:
            return JsonResponse({'error': 'Product ID missing'}, status=400)

        user = request.user
        cart_item = Cart.objects.filter(product_id=prod_id, user=user).first()

        if not cart_item:
            return JsonResponse({'error': 'Cart item does not exist'}, status=400)

        cart_item.quantity += 1
        cart_item.save()

        amount = sum(item.quantity * item.product.price for item in Cart.objects.filter(user=user))
        total_amount = amount + 40  # Including shipping

        return JsonResponse({'quantity': cart_item.quantity, 'amount': amount, 'totalamount': total_amount})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def minus_cart(request):
    if request.method == "GET":
        print("Minus cart API hit!")  # Debugging

        prod_id = request.GET.get("prod_id")
        print("Product ID:", prod_id)  # Debugging

        if not prod_id:
            return JsonResponse({'error': 'Product ID missing'}, status=400)

        user = request.user
        cart_item = Cart.objects.filter(product_id=prod_id, user=user).first()
        print("Cart Item:", cart_item)  # Debugging

        if not cart_item:
            return JsonResponse({'error': 'Cart item does not exist'}, status=400)

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            cart_item = None  # Ensure it's None after delete

        amount = sum(item.quantity * item.product.price for item in Cart.objects.filter(user=user))
        total_amount = amount + 40  

        print("Updated Quantity:", cart_item.quantity if cart_item else 0)  # Debugging
        print("New Amount:", amount, "New Total Amount:", total_amount)  # Debugging

        return JsonResponse({'quantity': cart_item.quantity if cart_item else 0, 'amount': amount, 'totalamount': total_amount})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def remove_cart(request):
    if request.method == "GET":
        prod_id = request.GET.get("prod_id")
        
        # Delete all cart items with the same product for the user
        Cart.objects.filter(product__id=prod_id, user=request.user).delete()
        
        # Recalculate the total amount
        cart_items = Cart.objects.filter(user=request.user)
        amount = sum(item.total_cost for item in cart_items)
        totalamount = amount + 40 if cart_items.exists() else 0  # Shipping included if cart is not empty

        return JsonResponse({"amount": amount, "totalamount": totalamount})


from django.shortcuts import render
from django.views import View

from django.views import View
from django.shortcuts import render, redirect
from .models import Customer

class PaymentView(View):  # Ensure class name is "PaymentView"
    def post(self, request):
        user = request.user
        address_id = request.POST.get('custid')  
        
        if not address_id:
            return redirect('checkout') 
        
        address = Customer.objects.get(id=address_id, user=user)
        return render(request, 'app/payment.html', {'address': address})
