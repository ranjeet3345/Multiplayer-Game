from django.shortcuts import render

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout  

# Signup view
def handlesignup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pass1']
        confirm_password = request.POST['pass2']

        if password != confirm_password:
            messages.error(request, "Password is not matching!!")
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.warning(request, "This Email already exists!!")
            return render(request, 'signup.html')

        user = User.objects.create_user(username=username, password=password)
        user.save()

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('/')

    return render(request, 'signup.html')

# Login view
def handlelogin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['pass1']

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Successfully logged in!")
            return redirect('/') 
        else:
            messages.error(request, "Invalid credentials!")
            return render(request, 'login.html')

    return render(request, 'login.html')

def handlelogout(request):
    logout(request)
    messages.success(request, "Successfully logged out!")
    return redirect('handlelogin')  


