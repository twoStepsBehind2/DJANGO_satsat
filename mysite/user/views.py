from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout as django_logout
from .models import RegisAcc, Products, Sale, SaleItem
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime
from django.db import transaction

# -------------------------------
# LOGOUT
# -------------------------------
def logout(request):
    django_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')


def logout_user(request):
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')


# -------------------------------
# LOGIN VIEW (Index Page)
# -------------------------------
def index(request):
    storage = messages.get_messages(request)
    storage.used = True  # Clear any old messages

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = RegisAcc.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name
            return redirect('dashboard')
        except RegisAcc.DoesNotExist:
            messages.error(request, 'Invalid username or password!')

    return render(request, 'users/index.html')


# -------------------------------
# DASHBOARD
# -------------------------------
def dashboard(request):
    return render(request, 'users/dashboard.html')


# -------------------------------
# PRODUCTS
# -------------------------------
def products(request):
    products = Products.objects.all()
    return render(request, 'users/products.html', {'products': products})


# -------------------------------
# CASHIER (main)
# -------------------------------
def cashier(request):
    products = Products.objects.filter(status='Available')
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = Decimal(0)

    # Build cart items
    for product_id, qty in cart.items():
        product = get_object_or_404(Products, id=product_id)
        subtotal = Decimal(product.price) * qty
        total_price += subtotal
        cart_items.append({
            'id': product.id,
            'brand': product.brand,
            'model': product.model,
            'price': product.price,
            'quantity': qty,
            'subtotal': subtotal
        })

    # Handle Add to Cart
    if request.method == 'POST' and 'add_to_cart' in request.POST:
        product_id = request.POST.get('product_id')
        qty = int(request.POST.get('quantity', 1))
        cart[str(product_id)] = cart.get(str(product_id), 0) + qty
        request.session['cart'] = cart
        messages.success(request, "Item added to cart.")
        return redirect('cashier')

    # Handle Checkout
    if request.method == 'POST' and 'checkout' in request.POST:
        amount_received = Decimal(request.POST.get('amount_received', '0'))
        payment_mode = request.POST.get('payment_mode', 'Cash')
        total = Decimal(total_price)

        if amount_received < total:
            messages.error(request, "❌ Insufficient amount! Please enter enough money.")
            return redirect('cashier')

        change = amount_received - total

        # Save sale and update stock
        with transaction.atomic():
            sale = Sale.objects.create(
                date=datetime.now(),
                total_price=total,
                payment_mode=payment_mode,
                amount_received=amount_received,
                change=change
            )

            for item in cart_items:
                SaleItem.objects.create(
                    sale=sale,
                    product_id=item['id'],
                    quantity=item['quantity'],
                    subtotal=item['subtotal']
                )

                product = Products.objects.get(id=item['id'])
                product.quantity -= item['quantity']
                product.save()

        request.session['cart'] = {}  # clear cart
        messages.success(request, f"✅ Sale completed successfully! Change: ₱{change:.2f}")
        return redirect('cashier')

    return render(request, 'users/cashier.html', {
        'products': products,
        'cart_items': cart_items,
        'total_price': total_price,
    })


# -------------------------------
# OPTIONAL: Separate add_to_cart route
# -------------------------------
def add_to_cart(request, product_id):
    """Optional: separate URL handler for adding items"""
    cart = request.session.get('cart', {})
    product = get_object_or_404(Products, id=product_id)
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    messages.success(request, f"{product.brand} {product.model} added to cart.")
    return redirect('cashier')
