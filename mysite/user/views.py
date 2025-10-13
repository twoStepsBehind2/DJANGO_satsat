from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import RegisAcc
from django.contrib.auth.hashers import make_password
from django.contrib.auth import logout as django_logout
from .models import Products

def logout(request):
    # Clear all session data
    django_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')


# -------------------------------
# LOGIN VIEW (Index Page)
# -------------------------------
def index(request):
    # ✅ CLEAR ANY OLD MESSAGES (like "Welcome, username")
    storage = messages.get_messages(request)
    storage.used = True   # Clears messages completely

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


def logout_user(request):
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect('index')


# DASHBOARD
# -------------------------------

def dashboard(request):
    # ❌ Remove messages.success(...). Keep the greeting inside the template only.
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
# SIGNUP VIEW (Register New Account)
# -------------------------------
def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        position = request.POST.get('position', '').strip()
        user_image = request.FILES.get('user_image')

        # Basic validation
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

        # Hash the password before saving
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

    # GET: show sign up form
    return render(request, 'users/signup.html')



def products(request):
    # Fetch all product records
    product_list = Products.objects.all()

    # Render to template
    return render(request, 'users/products.html', {'products': product_list})