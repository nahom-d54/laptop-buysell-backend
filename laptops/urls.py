from .views import (
    LaptopResourceView,
    ReviewRetrieveUpdateDestroyAPIView,
    ReviewList,
    ChatsResourceView,
    ChatPosts,
)
from rest_framework.routers import DefaultRouter
from django.urls import path

router = DefaultRouter()
router.register("laptops", LaptopResourceView, basename="laptop")
router.register("chats", ChatsResourceView, basename="chat")

urlpatterns = [
    path("reviews", ReviewList.as_view(), name="review-list"),
    path(
        "reviews/<int:id>",
        ReviewRetrieveUpdateDestroyAPIView.as_view(),
        name="review-get-update-delete",
    ),
    path("chat/<str:channel_id>", ChatPosts.as_view(), name="chat-posts"),
]

urlpatterns += router.urls
