from django.core.management.base import BaseCommand
from laptops.tasks import start_scheduler


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Put here some script to get the data from api service and store it into your models.
        start_scheduler()
