from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to my Django app!")

def about(request):
    return render(request, 'about.html')