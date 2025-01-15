from django.contrib import admin
from laptops.models import TelegramChat, LaptopPost, SimilarityScore

# Register your models here.
admin.site.register([TelegramChat, LaptopPost, SimilarityScore])
