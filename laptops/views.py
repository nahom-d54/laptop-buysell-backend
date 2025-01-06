from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import LaptopPost
from .serializers import LaptopPostSerializer
from rest_framework.pagination import PageNumberPagination


class LaptopResourceView(ReadOnlyModelViewSet):
    queryset = LaptopPost.objects.all()
    serializer_class = LaptopPostSerializer
    permission_classes = []
    authentication_classes = []
    pagination_class = PageNumberPagination
