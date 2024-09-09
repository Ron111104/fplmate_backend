# hello.py
from django.shortcuts import render

def hello(request):
    return render(request, 'landing.html')
