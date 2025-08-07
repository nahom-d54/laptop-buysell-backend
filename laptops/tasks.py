import asyncio
from pyrogram import Client
from django.conf import settings
from django.utils import timezone
from .models import LaptopPost, TelegramChat, LaptopImage, MentionTracker
from pyrogram.errors import FloodWait
from pyrogram.types import Dialog
from typing import List
import re
import json
import google.generativeai as genai
import time
from collections import deque

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from asgiref.sync import sync_to_async
from itertools import cycle
from django.core.files.base import ContentFile
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


class AsyncRateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.request_times = deque()

    async def check_and_wait(self):
        current_time = time.time()

        # Remove outdated request timestamps
        while (
            self.request_times
            and current_time - self.request_times[0] > self.window_seconds
        ):
            self.request_times.popleft()

        # Check if the rate limit is exceeded
        if len(self.request_times) >= self.max_requests:
            wait_time = self.window_seconds - (current_time - self.request_times[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        # Log the current request
        self.request_times.append(time.time())


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        """
        Initialize the rate limiter.
        :param max_requests: Maximum number of requests allowed in the time window.
        :param window_seconds: Time window in seconds.
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = deque()  # Track timestamps of requests

    def check_and_wait(self):
        """
        Check the current rate limit usage and sleep if the limit has been reached.
        """
        current_time = time.time()

        # Remove timestamps outside the current window
        while self.requests and self.requests[0] < current_time - self.window_seconds:
            self.requests.popleft()

        if len(self.requests) >= self.max_requests:
            # Calculate sleep time until the oldest request falls out of the window
            sleep_time = self.window_seconds - (current_time - self.requests[0])
            print(f"Rate limit reached. Sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)

        # Record the new request timestamp
        self.requests.append(current_time)


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


key_pool = cycle(settings.GEMENI_API_KEY)


async def process_product(product):
    api_key = next(key_pool)

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-1.5-flash", system_instruction=ai_system_prompt
    )
    if not product:
        return False, {}

    status, verified_product = False, {}
    rate_limiter = AsyncRateLimiter(max_requests=42, window_seconds=60)  # 15 RPM

    try:
        # Wait for rate limiter
        await rate_limiter.check_and_wait()
    except Exception as e:
        logger.error(f"Rate limiter failed: {str(e)}")
        return status, verified_product  # Return failure in case of rate limiter issue

    try:
        # Generate content with genai
        response = await model.generate_content_async(product)
        json_response = get_json_response(response.text)

        # Parse and verify the response
        final_response = json.loads(json_response)
        status, verified_product = verify_laptop_dict(final_response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
    except Exception as e:
        logger.error(f"Error in genai processing or verification: {str(e)}")

    return status, verified_product


@sync_to_async
def get_last_message_from_db(channel_id):
    return LaptopPost.objects.filter(channel_id=channel_id).order_by("-post_id").first()


@sync_to_async
def get_channel_list():
    return list(TelegramChat.objects.all())


async def download_mediagroup_images(
    app: Client, message_id: str | int, channel_id: str | int
) -> List[ContentFile]:
    media_group_photos = []

    try:
        media_group = await app.get_media_group(channel_id, message_id)
        for media in media_group:
            if media.photo:
                try:
                    file_bytes = await app.download_media(
                        media.photo.file_id, in_memory=True
                    )
                    file_bytes.seek(0)
                    media_message_id = media.id

                    # Create a unique filename for the photo
                    file_name = f"telegram_photo_{media_message_id}{channel_id}.jpg"

                    # Save the file as a Django FileField

                    profile_photo_file = ContentFile(file_bytes.read(), name=file_name)
                    media_group_photos.append(profile_photo_file)
                except Exception as e:
                    print(f"Error downloading photo: {str(e)}")
    except Exception as e:
        logger.error(f"Error downloading media group images: {str(e)}")

    return media_group_photos


async def scrape_laptops_async():
    logger.info("Starting to scrape telegram channels")
    app = Client(
        "LaptopScraper",
        api_id=settings.TELEGRAM_API_ID,
        api_hash=settings.TELEGRAM_API_HASH,
        session_string=settings.TELEGRAM_SESSIONS,
    )
    # channels = settings.TELEGRAM_CHANNELS
    channels = await get_channel_list()

    max_messages = 20

    try:
        async with app:
            for channel in channels:
                logger.info(f"Processing channel: {channel}")

                last_message_from_db = await get_last_message_from_db(
                    channel_id=channel.channel_id
                )

                last_post_id = (
                    last_message_from_db.post_id if last_message_from_db else 0
                )
                messages_with_captions = 0
                last_message_id = 0
                track = set()

                while messages_with_captions < max_messages:
                    should_break = False
                    try:
                        async for message in app.get_chat_history(
                            chat_id=channel.channel_id,
                            limit=50,
                            offset_id=last_message_id,
                        ):
                            if message.id in track:
                                # it will stop it if end of channel messsage
                                should_break = True
                            track.add(message.id)

                            if message.id <= last_post_id:
                                logger.info(
                                    f"Skipping message already processed: {message.id}"
                                )
                                should_break = True
                                break

                            logger.info(f"Processing message: {message.id}")
                            if message.caption:
                                messages_with_captions += 1
                            else:
                                continue

                            caption = message.caption

                            status, processed_product = await process_product(caption)

                            if status:
                                try:
                                    post = await sync_to_async(
                                        LaptopPost.objects.update_or_create
                                    )(
                                        channel_name=message.sender_chat.title
                                        if message.sender_chat
                                        else "Unknown",
                                        posted_at=timezone.make_aware(message.date),
                                        post_id=message.id,
                                        defaults=processed_product,
                                        channel_id=channel,
                                    )
                                    laptop_post_photos = (
                                        await download_mediagroup_images(
                                            app, message.id, message.sender_chat.id
                                        )
                                    )
                                    try:
                                        for photo in laptop_post_photos:
                                            await sync_to_async(
                                                LaptopImage.objects.create
                                            )(post=post[0], image=photo)

                                    except Exception as e:
                                        logger.error(
                                            f"Error saving laptop image to database: {str(e)}"
                                        )
                                        raise e

                                except Exception as e:
                                    logger.error(
                                        f"Error saving product to database: {str(e)}"
                                    )
                                    raise e
                            else:
                                logger.error(
                                    f"Error processing product: {processed_product}, {caption}"
                                )

                            last_message_id = message.id
                            if messages_with_captions >= max_messages:
                                break

                    except FloodWait as e:
                        logger.info(
                            f"Rate limit exceeded. Waiting for {e.value} seconds..."
                        )
                        await asyncio.sleep(
                            e.value
                        )  # Wait for the required time before retrying
                        continue
                    except Exception as e:
                        logger.error(f"Error processing channel: {str(e)}")
                        break

                    if should_break:
                        break

                    if last_message_id is None:
                        break

                # customize based on the channel so i might need to make it dynamic

    except ValueError as e:
        logger.error(f"Error processing channel : {str(e)}")
    except KeyError as e:
        logger.error(f"KeyError processing channel : {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error processing channel : {str(e)}")


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


@sync_to_async
def save_mention_tracker(channel, message_id, mention_text, unread_count):
    """Save mention tracker data to database"""
    try:
        mention, created = MentionTracker.objects.update_or_create(
            channel=channel,
            message_id=message_id,
            defaults={
                "mention_text": mention_text,
                "unread_count": unread_count,
                "is_processed": False,
                "is_read": False,
            },
        )
        return mention, created
    except Exception as e:
        logger.error(f"Error saving mention tracker: {str(e)}")
        return None, False


@sync_to_async
def mark_mention_processed(mention_id):
    """Mark a mention as processed"""
    try:
        mention = MentionTracker.objects.get(id=mention_id)
        mention.is_processed = True
        mention.processed_at = timezone.now()
        mention.save()
        return True
    except MentionTracker.DoesNotExist:
        logger.error(f"Mention with id {mention_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error marking mention as processed: {str(e)}")
        return False


@sync_to_async
def mark_mention_read(mention_id):
    """Mark a mention as read"""
    try:
        mention = MentionTracker.objects.get(id=mention_id)
        mention.is_read = True
        mention.marked_read_at = timezone.now()
        mention.save()
        return True
    except MentionTracker.DoesNotExist:
        logger.error(f"Mention with id {mention_id} not found")
        return False
    except Exception as e:
        logger.error(f"Error marking mention as read: {str(e)}")
        return False


@sync_to_async
def get_unprocessed_mentions():
    """Get unprocessed mentions from database"""
    return list(MentionTracker.objects.filter(is_processed=False))


async def process_mentions_for_dialog(app: Client, dialog: Dialog, channel):
    """Process mentions for a specific dialog"""
    try:
        # Check if there are unread mentions
        if dialog.unread_mentions_count > 0:
            logger.info(f"Found {dialog.unread_mentions_count} unread mentions in {channel.title}")
            
            # Get recent messages that might contain mentions
            async for message in app.get_chat_history(
                chat_id=dialog.chat.id,
                limit=dialog.unread_mentions_count * 2  # Get a few more to ensure we catch all
            ):
                # Check if message contains mentions (looking for @mentions or replies)
                mention_text = ""
                if message.text:
                    mention_text = message.text
                elif message.caption:
                    mention_text = message.caption
                
                if mention_text and ("@" in mention_text or message.reply_to_message):
                    # Save the mention to track it
                    mention, created = await save_mention_tracker(
                        channel=channel,
                        message_id=message.id,
                        mention_text=mention_text,
                        unread_count=dialog.unread_mentions_count
                    )
                    
                    if created:
                        logger.info(f"New mention tracked: {message.id} in {channel.title}")
                    
                    # Process the mention (similar to existing message processing)
                    if mention_text:
                        status, processed_product = await process_product(mention_text)
                        
                        if status:
                            # Save as laptop post if it's a valid laptop mention
                            try:
                                await sync_to_async(LaptopPost.objects.update_or_create)(
                                    channel_name=dialog.chat.title or "Unknown",
                                    posted_at=timezone.make_aware(message.date),
                                    post_id=message.id,
                                    defaults=processed_product,
                                    channel_id=channel,
                                )
                                logger.info(f"Processed mention as laptop post: {message.id}")
                            except Exception as e:
                                logger.error(f"Error saving mention as laptop post: {str(e)}")
                        
                        # Mark as processed
                        if mention:
                            await mark_mention_processed(mention.id)
                    
            # Mark dialog as read to clear unread mentions count
            try:
                await app.read_chat_history(dialog.chat.id)
                logger.info(f"Marked chat history as read for {channel.title}")
                
                # Update all mentions for this channel as read
                unprocessed_mentions = await get_unprocessed_mentions()
                for mention in unprocessed_mentions:
                    if mention.channel_id == channel.channel_id:
                        await mark_mention_read(mention.id)
                        
            except Exception as e:
                logger.error(f"Error marking chat as read: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error processing mentions for dialog: {str(e)}")


async def listen_to_mentions_async():
    """Listen to channels and process unread mentions using Dialog"""
    logger.info("Starting to listen for mentions in telegram channels")
    
    app = Client(
        "MentionListener",
        api_id=settings.TELEGRAM_API_ID,
        api_hash=settings.TELEGRAM_API_HASH,
        session_string=settings.TELEGRAM_SESSIONS,
    )
    
    channels = await get_channel_list()
    
    try:
        async with app:
            # Get all dialogs (conversations)
            async for dialog in app.get_dialogs():
                # Find matching channel in our database
                matching_channel = None
                for channel in channels:
                    if dialog.chat.id == channel.channel_id:
                        matching_channel = channel
                        break
                
                if matching_channel:
                    await process_mentions_for_dialog(app, dialog, matching_channel)
                    
                    # Add a small delay to avoid hitting rate limits
                    await asyncio.sleep(0.5)
                    
    except Exception as e:
        logger.error(f"Error in mention listener: {str(e)}")


def listen_to_mentions():
    """Synchronous wrapper for mention listening"""
    asyncio.run(listen_to_mentions_async())
