from django.shortcuts import render, redirect
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from .models import Post
from datetime import datetime


def register(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        form = CreateUserForm()

        if request.method == "POST":
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Account was created for " + form.cleaned_data.get("username"))

                return redirect("login")
            else:
                messages.error(request, "An error occurred while creating the account, please try again.")
        else:
            form = CreateUserForm()
        context = {'form': form}
        return render(request, "register.html", context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect("home")
    else:
        if request.method == "POST":
            username = request.POST.get("username")
            password = request.POST.get("password")

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                messages.error(request, "Username or password is incorrect, please try again.")

        context = {}
        return render(request, "login.html", context)


def logoutUser(request):
    logout(request)
    return redirect("login")


@login_required(login_url="login")
def home(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})


@login_required(login_url="login")
def explore(request):
    return render(request, "explore.html")


@login_required(login_url="login")
def notifications(request):
    return render(request, "notifications.html")


@login_required(login_url="login")
def boards(request):
    return render(request, "boards.html")


@login_required(login_url="login")
def polls(request):
    return render(request, "polls.html")


@login_required(login_url="login")
def discussions(request):
    return render(request, "discussions.html")


def news(request):
    return render(request, "news.html")


@login_required(login_url="login")
def create(request):

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()



    return render(request, 'create.html', {'form': form})
