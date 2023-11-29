from django.shortcuts import render

from api.models import UploadedFile
from api.serializers import UploadedFileSerializer


def home(request):
    return render(request, "dataapplication/home.html", {"page": "home"})


def data(request):
    query_set = UploadedFile.objects.all()
    uploadedfiles = UploadedFileSerializer(query_set, many=True).data
    return render(
        request,
        "dataapplication/data.html",
        {"page": "data", "uploadedfiles": uploadedfiles},
    )


def plot(request):
    query_set = UploadedFile.objects.all()
    uploaded_files = UploadedFileSerializer(query_set, many=True).data
    return render(
        request,
        "dataapplication/plot.html",
        {"page": "plot", "uploaded_files": uploaded_files},
    )
