from django.urls import path
from .views import LaptopPostListView

urlpatterns = [
    path('laptops/', LaptopPostListView.as_view(), name='laptop-list'),
]