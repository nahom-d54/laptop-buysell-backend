from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import LaptopPost, Review
from .serializers import LaptopPostSerializer, ReviewSerializer
from rest_framework.pagination import PageNumberPagination
from .viewsets import CreateListRetriveUpdate


class LaptopResourceView(ReadOnlyModelViewSet):
    queryset = LaptopPost.objects.all()
    serializer_class = LaptopPostSerializer
    permission_classes = []
    authentication_classes = []
    pagination_class = PageNumberPagination


class ReviewViewset(CreateListRetriveUpdate):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = PageNumberPagination
