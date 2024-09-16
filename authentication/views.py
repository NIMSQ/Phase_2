from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from Project import settings
from django.core.mail import send_mail

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
def home(request):
    
    return render(request, 'index.html')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # Check if passwords match
        if pass1 != pass2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        
        if User.objects.filter(username=username):
            messages.error(request, "Username already exists.")
            return redirect('signup')   
               
        if User.objects.filter(email=email):
            messages.error(request, "Email already exists.")   
            return redirect('signup')

            
       
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.save()
        return redirect('signin')



    return render(request, 'signup.html')


def signin(request):
    if request.method == 'POST':
        # Corrected request.post to request.POST
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        # Authenticate user
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            # Log in the user and redirect to home page with user's first name
            login(request, user)
            fname = user.first_name
            return render(request, 'index.html', {'fname': fname})
        
        else:
            # Error message for invalid credentials
             messages.error(request, "the username or password in not correct")
             return redirect('signin')  # Redirecting back to sign-in page
            
    return render(request, 'signin.html')

def signout(request):
    logout(request)
    messages.success(request, "Loged Out Successfully!")
    return redirect('home')


def offer(request):
    
    return render(request, 'offer.html')