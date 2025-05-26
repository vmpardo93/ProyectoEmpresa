from django.shortcuts import render

def about_us(request):
    return render(request, 'home/about_us.html') 