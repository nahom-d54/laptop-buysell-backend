from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import LaptopPost, Review, TelegramChat
from .serializers import LaptopPostSerializer, ReviewSerializer, ChatSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django.db.models import Q


class LaptopResourceView(ReadOnlyModelViewSet):
    queryset = LaptopPost.objects.all()
    serializer_class = LaptopPostSerializer
    permission_classes = []
    authentication_classes = []
    pagination_class = PageNumberPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Add `is_single_retrieval` flag based on the request
        context["is_single_retrieval"] = self.action == "retrieve"
        return context

    def get_queryset(self):
        query = self.request.query_params.get("q", "")
        retrieve_null_price = self.request.query_params.get("null_price", False)
        tokens = query.split()

        query_types = self.request.query_params.get("type", "").split(",")
        query_filter_types = {
            "storage": Q(storage__icontains=query),
            "processor": Q(processor__icontains=query),
            "graphics": Q(graphics__icontains=query),
            "display": Q(display__icontains=query),
            "ram": Q(ram__icontains=query),
            "battrey": Q(battrey__icontains=query),
            "status": Q(status__icontains=query),
            "color": Q(color__icontains=query),
            "description": Q(description__icontains=query),
        }

        # query_filter = Q(title__icontains=query) | Q(description__icontains=query)
        query_filter = Q()
        for token in tokens:
            query_filter &= Q(title__icontains=token) | Q(description__icontains=token)
        if query_types:
            for query_type in query_types:
                if query_type in query_filter_types:
                    query_filter |= query_filter_types.get(query_type)

        return (
            super()
            .get_queryset()
            .filter(query_filter, price__isnull=retrieve_null_price)
            if query
            else super().get_queryset().filter(price__isnull=retrieve_null_price)
        )


class ReviewList(ListAPIView):
    queryset = Review.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = ReviewSerializer


class ReviewRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    pagination_class = PageNumberPagination
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_url_kwarg = "id"


class ChatsResourceView(ReadOnlyModelViewSet):
    queryset = TelegramChat.objects.all()
    serializer_class = ChatSerializer
    permission_classes = []
    authentication_classes = []
    pagination_class = PageNumberPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Add `is_single_retrieval` flag based on the request
        context["is_single_retrieval"] = self.action == "retrieve"
        return context


class ChatPosts(ListAPIView):
    queryset = LaptopPost.objects.all()
    serializer_class = LaptopPostSerializer
    pagination_class = PageNumberPagination
    permission_classes = []
    authentication_classes = []

    def get_queryset(self):
        return super().get_queryset().filter(channel_id=self.kwargs.get("channel_id"))
