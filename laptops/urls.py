from .views import LaptopResourceView, ReviewViewset
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register("laptops", LaptopResourceView, basename="laptop")
router.register("reviews", ReviewViewset, basename="review")


urlpatterns = []

urlpatterns += router.urls
