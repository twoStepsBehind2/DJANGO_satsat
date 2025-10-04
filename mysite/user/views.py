from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import RegisAcc


def index(request):
    return render(request, 'users/index.html')

def dashboard(request):
    return render(request, 'users/dashboard.html')

def userlist(request):
    if request.method == 'POST':
        # Handle Add User form
        name = request.POST.get('name')
        username = request.POST.get('username')
        password = request.POST.get('password')   # ⚠️ should be hashed for real apps
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
        return redirect('userlist')  # Refresh page after submit

    # Display all users
    users = RegisAcc.objects.all()
    return render(request, 'users/userlist.html', {'users': users})

def edit_user(request, user_id):
    user = get_object_or_404(RegisAcc, id=user_id)

    if request.method == 'POST':
        user.name = request.POST.get('name')
        user.username = request.POST.get('username')

        # Only update password if provided
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
