from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home_page"),
    path("data", views.data, name="data_page"),
    path("plot", views.plot, name="plot_page"),
]
