from django.contrib import admin
from laptops.models import TelegramChat, LaptopPost

# Register your models here.
admin.site.register([TelegramChat, LaptopPost])
