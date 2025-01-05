from rest_framework import generics
from .models import LaptopPost
from .serializers import LaptopPostSerializer

class LaptopPostListView(generics.ListAPIView):
    queryset = LaptopPost.objects.all()
    serializer_class = LaptopPostSerializer
