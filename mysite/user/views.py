from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'users/index.html')

def dashboard(request):
    return render(request, 'users/dashboard.html')

def userlist(request):
    return render(request, 'users/userlist.html')
