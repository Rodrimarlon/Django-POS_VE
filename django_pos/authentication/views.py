# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from .models import Profile # Import Profile model


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid username or password!'
        else:
            msg = 'An error occurred!.'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_user(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a profile for the new user with default cashier role
            Profile.objects.create(user=user, role='cashier')
            # You can add a success message here if you want
            return redirect("authentication:login")
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form})