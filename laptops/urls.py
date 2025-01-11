from .views import LaptopResourceView, ReviewRetrieveUpdateDestroyAPIView, ReviewList
from rest_framework.routers import DefaultRouter
from django.urls import path


router = DefaultRouter()

router.register("laptops", LaptopResourceView, basename="laptop")


urlpatterns = [
    path("reviews", ReviewList.as_view(), name="review-list"),
    path(
        "reviews/:id",
        ReviewRetrieveUpdateDestroyAPIView.as_view(),
        name="review-get-update-delete",
    ),
]

urlpatterns += router.urls
