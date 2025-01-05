from pyrogram import Client
from django.conf import settings
from .models import LaptopPost



ai_system_prompt = """
Parse the following text into JSON format to match the provided model fields. The JSON should contain the following keys:

title: A short title summarizing the laptop.
storage: Details about the laptop's storage (e.g., SSD or HDD and capacity).
processor: Details about the processor (e.g., brand, model, and generation).
graphics: Information about the graphics card (e.g., brand and model).
display: Specifications of the display (e.g., size, resolution, type).
ram: Details about the RAM (e.g., capacity and type).
battrey: Information about the battery (e.g., capacity, backup time).
status: The condition of the laptop (e.g., new, used, refurbished).
color: The color of the laptop.
description: A detailed description of the laptop.
price: The price of the laptop (if available).
If any details are missing in the input, use null or an empty string. Ensure the JSON is well-formed and matches the following structure:

{
  "title": "Example Title",
  "storage": "512GB SSD",
  "processor": "Intel Core i7 10th Gen",
  "graphics": "NVIDIA GTX 1650",
  "display": "15.6-inch FHD",
  "ram": "16GB DDR4",
  "battrey": "6 hours backup",
  "status": "Used",
  "color": "Silver",
  "description": "A detailed description of the laptop.",
  "price": "$1200"
}
"""




def scrape_laptops():
    app = Client(settings.TELEGRAM_SESSIONS, api_id=settings.TELEGRAM_API_ID, api_hash=settings.TELEGRAM_API_HASH)

    channels = settings.TELEGRAM_CHANNELS
    
    with app:
        for channel in channels:
            messages = app.get_history(channel, limit=50)
            for message in messages:
                # customize based on the channel so i might need to make it dynamic

                # add an ai integration to parse the data into proper json output
                if message.text and "laptop" in message.text.lower():
                    LaptopPost.objects.update_or_create(
                        post_id=message.id,
                        defaults={
                            'title': message.text[:50],
                            'description': message.text,
                            'channel_name': channel,
                            'posted_at': message.date,
                        }
                    )
