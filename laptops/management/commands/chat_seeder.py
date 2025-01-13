from django.core.management.base import BaseCommand
import asyncio
from laptops.seeder import chat_seeder


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Put here some script to get the data from api service and store it into your models.
        event_loop = asyncio.get_event_loop()
        event_loop.run_until_complete(chat_seeder())
