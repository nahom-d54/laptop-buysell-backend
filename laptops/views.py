from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import LaptopPost, Review
from .serializers import LaptopPostSerializer, ReviewSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly


class LaptopResourceView(ReadOnlyModelViewSet):
    queryset = LaptopPost.objects.all()
    serializer_class = LaptopPostSerializer
    permission_classes = []
    authentication_classes = []
    pagination_class = PageNumberPagination


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
