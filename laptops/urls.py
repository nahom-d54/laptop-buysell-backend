from .views import LaptopResourceView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("laptops", LaptopResourceView, basename="laptop")


urlpatterns = []

urlpatterns += router.urls
