from django.urls import path
from . import views

urlpatterns = [
    path("", views.get_or_upload_datasets, name="get_or_upload_datasets"),
    path("<int:id>/compute", views.compute, name="compute"),
    path("<int:id>/plot", views.plot, name="plot"),
]
