import asyncio
from pyrogram import Client
from django.conf import settings
from django.utils import timezone
from .models import LaptopPost
from pyrogram.errors import FloodWait
import re
import json
import google.generativeai as genai


from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from asgiref.sync import sync_to_async

import logging

# Get the logger for your app
logger = logging.getLogger("laptops")


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


genai.configure(api_key=settings.GEMENI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash", system_instruction=ai_system_prompt)


def verify_laptop_dict(data):
    """
    Verify if the input dictionary matches the expected laptop data format.
    """
    # Define the required structure with field names and expected types
    expected_structure = {
        "title": str,
        "storage": (str, type(None)),
        "processor": (str, type(None)),
        "graphics": (str, type(None)),
        "display": (str, type(None)),
        "ram": (str, type(None)),
        "battrey": (str, type(None)),
        "status": (str, type(None)),
        "color": (str, type(None)),
        "description": (str, type(None)),
        "price": (str, type(None)),  # Price can be a string or None
    }

    cleaned_data = {}

    # Validate and clean the data
    for key, expected_type in expected_structure.items():
        if key in data and isinstance(data[key], expected_type):
            cleaned_data[key] = data[key]
        elif key in data:
            return (
                False,
                f"Key '{key}' has invalid type. Expected {expected_type}, got {type(data[key])}",
            )
        else:
            return False, f"Missing required key: {key}"

    return True, cleaned_data


def get_json_response(data):
    pattern = r"\{[^{}]*\}"
    match = re.findall(pattern, data)
    return match[0] if match else {}


def process_product(product):
    if not product:
        return False, {}
    response = model.generate_content(product)
    json_response = get_json_response(response.text)

    final_response = json.loads(json_response)

    status, verified_product = verify_laptop_dict(final_response)

    return status, verified_product


async def scrape_laptops_async():
    logger.info("Starting to scrape telegram channels")
    app = Client(
        "LaptopScraper",
        api_id=settings.TELEGRAM_API_ID,
        api_hash=settings.TELEGRAM_API_HASH,
        session_string=settings.TELEGRAM_SESSIONS,
    )
    channels = settings.TELEGRAM_CHANNELS

    max_messages = 20
    messages_with_captions = 0
    last_message_id = 0

    try:
        async with app:
            for channel in channels:
                while messages_with_captions < max_messages:
                    try:
                        async for message in app.get_chat_history(
                            channel, limit=50, offset_id=last_message_id
                        ):
                            if message.caption:
                                messages_with_captions += 1

                            caption = message.caption
                            status, processed_product = process_product(caption)
                            if status:
                                try:
                                    await sync_to_async(
                                        LaptopPost.objects.update_or_create
                                    )(
                                        channel_name=message.sender_chat.title
                                        if message.sender_chat
                                        else "Unknown",
                                        posted_at=timezone.make_aware(message.date),
                                        post_id=message.id,
                                        defaults=processed_product,
                                        channel_id=message.sender_chat.id,
                                    )
                                except Exception as e:
                                    logger.error(
                                        f"Error saving product to database: {str(e)}"
                                    )
                                    raise e
                            else:
                                logger.error(
                                    f"Error processing product: {processed_product}"
                                )

                            last_message_id = message.id
                            if len(messages_with_captions) >= max_messages:
                                break

                    except FloodWait as e:
                        print(f"Rate limit exceeded. Waiting for {e.value} seconds...")
                        await asyncio.sleep(
                            e.value
                        )  # Wait for the required time before retrying
                        continue

                    if last_message_id is None:
                        break

                # customize based on the channel so i might need to make it dynamic

    except ValueError as e:
        logger.error(f"Error processing channel {channel}: {str(e)}")
    except KeyError as e:
        logger.error(f"KeyError processing channel {channel}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error processing channel {channel}: {str(e)}")


def scrape_laptops():
    asyncio.run(scrape_laptops_async())


def start_scheduler():
    scheduler = BackgroundScheduler()
    interval_minute = settings.SCHEDULE_INTERVAL
    scheduler.add_job(
        scrape_laptops,
        trigger=IntervalTrigger(minutes=int(interval_minute)),
        id="Scrapelaptops",
        replace_existing=True,
    )
    scheduler.start()
