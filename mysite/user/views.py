from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout as django_logout
from .models import RegisAcc, Products
from django.db.models import Sum
from .models import Products





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
# USER LIST
# -------------------------------
def userlist(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')
        position = request.POST.get('position')
        user_image = request.FILES.get('user_image')

        new_user = RegisAcc(
            name=name,
            username=username,
            password=password,
            position=position,
            user_image=user_image if user_image else 'profile/image.png'
        )
        new_user.save()
        messages.success(request, f'User "{name}" added successfully!')
        return redirect('userlist')

    users = RegisAcc.objects.all()
    return render(request, 'users/userlist.html', {'users': users})


# -------------------------------
# EDIT USER
# -------------------------------
def edit_user(request, user_id):
    user = get_object_or_404(RegisAcc, id=user_id)
    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.username = request.POST.get('username')
        password = request.POST.get('password')
        if password:
            user.password = password
        user.position = request.POST.get('position')
        if 'user_image' in request.FILES:
            user.user_image = request.FILES['user_image']
        user.save()
        messages.success(request, f"User '{user.username}' updated successfully!")
        return redirect('userlist')
    return redirect('userlist')


# -------------------------------
# DELETE USER
# -------------------------------
def delete_user(request, user_id):
    user = get_object_or_404(RegisAcc, id=user_id)
    if request.method == 'POST':
        user.delete()
        messages.success(request, f"User '{user.username}' deleted successfully!")
        return redirect('userlist')
    return redirect('userlist')


# -------------------------------
# SIGNUP VIEW
# -------------------------------
def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        position = request.POST.get('position', '').strip()
        user_image = request.FILES.get('user_image')

        if not name or not username or not password or not position:
            messages.error(request, "All fields are required.")
            return redirect('signup')

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('signup')

        if position not in ['Admin', 'Cashier']:
            messages.error(request, "Invalid position selected.")
            return redirect('signup')

        if RegisAcc.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Choose another.")
            return redirect('signup')

        hashed_password = make_password(password)

        new_user = RegisAcc(
            name=name,
            username=username,
            password=hashed_password,
            position=position,
            user_image=user_image if user_image else 'profile/image.png'
        )
        new_user.save()
        messages.success(request, "Account created successfully! Please log in.")
        return redirect('index')

    return render(request, 'users/signup.html')


# -------------------------------
# PRODUCTS
# -------------------------------
def products(request):
    products = Products.objects.all()
    return render(request, 'users/products.html', {'products': products})


# -------------------------------
# ADD PRODUCT
# -------------------------------
def add_product(request):
    if request.method == 'POST':
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        product_condition = request.POST.get('product_condition')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        status = request.POST.get('status')

        Products.objects.create(
            brand=brand,
            model=model,
            product_condition=product_condition,
            quantity=quantity,
            price=price,
            status=status
        )
        messages.success(request, f"Product '{brand} {model}' added successfully!")
        return redirect('products')

    return render(request, 'users/add_product.html')

def delete_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Product '{product.brand} {product.model}' deleted successfully!")
        return redirect('products')
    return redirect('products')

def edit_product(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    if request.method == 'POST':
        product.brand = request.POST.get('brand')
        product.model = request.POST.get('model')
        product.product_condition = request.POST.get('product_condition')
        product.quantity = request.POST.get('quantity')
        product.price = request.POST.get('price')
        product.status = request.POST.get('status')
        product.save()

        messages.success(request, f"Product '{product.brand} {product.model}' updated successfully!")
        return redirect('products')

    # Render edit form with existing product data
    return render(request, 'users/edit_product.html', {'product': product})




def product_stock(request):
    products = Products.objects.all()

    total_products = products.count()
    total_quantity = products.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_value = sum([(p.quantity or 0) * (float(p.price) or 0) for p in products])
    low_stock = products.filter(quantity__lt=5)

    # add computed value for each product
    for p in products:
        p.total_value = (p.quantity or 0) * (float(p.price) or 0)

    context = {
        'products': products,
        'total_products': total_products,
        'total_quantity': total_quantity,
        'total_value': total_value,
        'low_stock': low_stock,
    }
    return render(request, 'users/product_stock.html', context)
