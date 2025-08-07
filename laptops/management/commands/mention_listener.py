from django.core.management.base import BaseCommand
import asyncio
from laptops.tasks import listen_to_mentions


class Command(BaseCommand):
    help = 'Listen to telegram channels for mentions and process them'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting mention listener for telegram channels...')
        )
        
        try:
            listen_to_mentions()
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('Mention listener stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error in mention listener: {str(e)}')
            )