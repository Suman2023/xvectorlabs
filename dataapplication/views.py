from django.shortcuts import render

# from api.models import UploadedFile

# Create your views here.


def home(request):
    return render(request, "dataapplication/home.html", {"page": "home"})


def data(request):
    return render(request, "dataapplication/data.html", {"page": "data"})


def plot(request):
    return render(request, "dataapplication/plot.html", {"page": "plot"})
