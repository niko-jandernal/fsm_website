from django.shortcuts import render


# Create your views here.

def home(request):
    return render(request, "home.html")


def explore(request):
    return render(request, "explore.html")


def notifications(request):
    return render(request, "notifications.html")


def boards(request):
    return render(request, "boards.html")


def polls(request):
    return render(request, "polls.html")


def discussions(request):
    return render(request, "discussions.html")


def news(request):
    return render(request, "news.html")


def create(request):
    return render(request, "create.html")


def signin(request):
    return render(request, "signin.html")
