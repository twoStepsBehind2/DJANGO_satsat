from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout as django_logout
from .models import RegisAcc, Products, Sale, SaleItem
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import io
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

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
    storage.used = True  # clear old messages

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = RegisAcc.objects.get(username=username, password=password)
            request.session['user_id'] = user.id
            request.session['user_name'] = user.name
            request.session['user_position'] = user.position  # store user role

            if user.position == 'Admin':
                return redirect('dashboard')
            elif user.position == 'Cashier':
                return redirect('cashier')
            else:
                messages.error(request, 'Unauthorized role.')
                return redirect('index')

        except RegisAcc.DoesNotExist:
            messages.error(request, 'Invalid username or password!')

    return render(request, 'users/index.html')


# -------------------------------
# DASHBOARD
# -------------------------------
def dashboard(request):
    return render(request, 'users/dashboard.html')


# -------------------------------
# USER LIST / CRUD
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

        new_user = RegisAcc(
            name=name,
            username=username,
            password=password,
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

    return render(request, 'users/edit_product.html', {'product': product})


# -------------------------------
# STOCK / REPORTS
# -------------------------------
def product_stock(request):
    products = Products.objects.all()

    total_products = products.count()
    total_quantity = products.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_value = sum([(p.quantity or 0) * (float(p.price) or 0) for p in products])
    low_stock = products.filter(quantity__lt=5)

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


# -------------------------------
# CASHIER
# -------------------------------
def cashier(request):
    cart = request.session.get('cart', {})

    # Search (brand + model)
    query = request.GET.get('q', '')
    products_list = Products.objects.filter(status='Available')
    if query:
        products_list = products_list.filter(brand__icontains=query) | Products.objects.filter(status='Available', model__icontains=query)

    cart_items = []
    total_price = Decimal('0.00')
    total_items = 0

    products_in_cart = Products.objects.filter(id__in=cart.keys())
    for product in products_in_cart:
        qty = cart.get(str(product.id), 0)
        subtotal = Decimal(qty) * product.price
        total_price += subtotal
        total_items += qty
        cart_items.append({
            'id': product.id,
            'brand': product.brand,
            'model': product.model,
            'quantity': qty,
            'price': product.price,
            'subtotal': subtotal,
        })

    # Payment processing - POST
    if request.method == 'POST' and 'payment_mode' in request.POST:
        payment_mode = request.POST.get('payment_mode')
        amount_received = Decimal(request.POST.get('amount_received', '0'))

        if amount_received < total_price:
            messages.error(request, "Insufficient payment. Transaction canceled.")
            return redirect('cashier')

        try:
            with transaction.atomic():
                # stock check
                for item in cart_items:
                    product = Products.objects.select_for_update().get(id=item['id'])
                    if product.quantity < item['quantity']:
                        messages.error(request, f"Insufficient stock for {product.brand} {product.model}.")
                        return redirect('cashier')

                # create sale
                sale = Sale.objects.create(
                    payment_mode=payment_mode,
                    amount_received=amount_received,
                    total_price=total_price,
                    change=amount_received - total_price,
                    sale_date=timezone.now()
                )

                # create sale items and deduct stock
                for item in cart_items:
                    SaleItem.objects.create(
                        sale=sale,
                        product_id=item['id'],
                        quantity=item['quantity'],
                        price=item['price']
                    )
                    # deduct stock (optional here or handled in SaleItem.save)
                    prod = Products.objects.get(id=item['id'])
                    prod.quantity = prod.quantity - item['quantity']
                    prod.save()

                # update totals & clear cart
                sale.update_totals()
                sale.refresh_from_db()
                request.session['cart'] = {}
                request.session.modified = True

                # return PDF receipt for download
                return generate_receipt_pdf(request, sale.id)

        except Exception as e:
            messages.error(request, f"Transaction failed: {str(e)}")
            return redirect('cashier')

    context = {
        'products': products_list,
        'cart_items': cart_items,
        'total_price': total_price,
        'total_items': total_items,
        'query': query,
    }
    return render(request, 'users/cashier.html', context)


# -------------------------------
# CART HELPERS
# -------------------------------
def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    request.session.modified = True
    messages.success(request, f"Added {product.brand} {product.model} to cart.")
    return redirect('cashier')


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
    return redirect('cashier')


def clear_cart(request):
    request.session['cart'] = {}
    request.session.modified = True
    messages.info(request, "Cart cleared.")
    return redirect('cashier')


# -------------------------------
# RECEIPT (PDF)
# -------------------------------
def generate_receipt_pdf(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    items = SaleItem.objects.filter(sale=sale)

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    left_margin = 15 * mm
    right_margin = width - 15 * mm
    y = height - 20 * mm

    # Header
    p.setFont("Helvetica-Bold", 14)
    p.drawString(left_margin, y, "GPU Market")
    p.setFont("Helvetica", 9)
    y -= 6 * mm
    p.drawString(left_margin, y, "Receipt")
    y -= 8 * mm

    # Meta
    p.setFont("Helvetica", 9)
    cashier_name = request.session.get('user_name', 'Unknown')
    p.drawString(left_margin, y, f"Cashier: {cashier_name}")
    p.drawRightString(right_margin, y, f"Sale ID: {sale.id}")
    y -= 5 * mm
    sale_dt = sale.sale_date if sale.sale_date else timezone.now()
    p.drawString(left_margin, y, f"Date: {sale_dt.strftime('%Y-%m-%d %H:%M:%S')}")
    y -= 8 * mm

    # Table header
    p.setFont("Helvetica-Bold", 9)
    p.drawString(left_margin, y, "Item")
    p.drawRightString(left_margin + 70*mm, y, "Qty")
    p.drawRightString(left_margin + 95*mm, y, "Price")
    p.drawRightString(right_margin, y, "Subtotal")
    y -= 5 * mm
    p.setLineWidth(0.3)
    p.line(left_margin, y, right_margin, y)
    y -= 4 * mm

    # Items
    p.setFont("Helvetica", 9)
    for si in items:
        try:
            product = si.product
            name = f"{product.brand} {product.model}"
        except Exception:
            prod = Products.objects.filter(id=si.product_id).first()
            name = f"{prod.brand} {prod.model}" if prod else f"Product {si.product_id}"

        max_name_chars = 30
        if len(name) > max_name_chars:
            name = name[:max_name_chars-3] + "..."

        qty = int(si.quantity)
        price = si.price
        subtotal = (Decimal(qty) * Decimal(price))

        p.drawString(left_margin, y, name)
        p.drawRightString(left_margin + 70*mm, y, str(qty))
        p.drawRightString(left_margin + 95*mm, y, f"₱{price:.2f}")
        p.drawRightString(right_margin, y, f"₱{subtotal:.2f}")
        y -= 5 * mm

        if y < 30*mm:
            p.showPage()
            y = height - 20*mm
            p.setFont("Helvetica", 9)

    y -= 4 * mm
    p.line(left_margin, y, right_margin, y)
    y -= 6 * mm

    # Totals
    p.setFont("Helvetica-Bold", 10)
    p.drawRightString(right_margin - 40*mm, y, "Total:")
    p.drawRightString(right_margin, y, f"₱{sale.total_price:.2f}")
    y -= 6 * mm

    p.setFont("Helvetica", 9)
    p.drawRightString(right_margin - 40*mm, y, "Amount Received:")
    p.drawRightString(right_margin, y, f"₱{sale.amount_received:.2f}")
    y -= 5 * mm

    p.drawRightString(right_margin - 40*mm, y, "Change:")
    p.drawRightString(right_margin, y, f"₱{sale.change:.2f}")
    y -= 10 * mm

    p.setFont("Helvetica-Oblique", 9)
    p.drawCentredString((left_margin + right_margin)/2, y, "Thank you for shopping at GPU Market!")
    y -= 8 * mm

    p.showPage()
    p.save()

    buffer.seek(0)
    filename = f"receipt_{sale.id}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=\"{filename}\"'
    return response


# -------------------------------
# REPORTS / SALES
# -------------------------------
def dashboard(request):
    return render(request, 'users/dashboard.html')


def total_sales_view(request):
    sales = Sale.objects.all().order_by('-sale_date')
    total_sales_amount = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
    total_products_sold = SaleItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    total_transactions = sales.count()

    context = {
        'sales': sales,
        'total_sales_amount': total_sales_amount,
        'total_products_sold': total_products_sold,
        'total_transactions': total_transactions,
    }
    return render(request, 'users/totalsales.html', context)


def stock_sold_view(request):
    sold_items = SaleItem.objects.select_related('product', 'sale').order_by('-sale__sale_date')
    total_products_sold = sold_items.aggregate(total=Sum('quantity'))['total'] or 0
    total_sales_value = sold_items.aggregate(
        total=Sum(ExpressionWrapper(F('quantity') * F('price'), output_field=DecimalField(max_digits=12, decimal_places=2)))
    )['total'] or 0
    total_brands_sold = sold_items.values('product__brand').distinct().count()

    context = {
        'sold_items': sold_items,
        'total_products_sold': total_products_sold,
        'total_sales_value': total_sales_value,
        'total_brands_sold': total_brands_sold,
    }
    return render(request, 'users/stocksold.html', context)
