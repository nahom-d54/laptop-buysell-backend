from laptops.models import TelegramChat
from pyrogram import Client
from django.conf import settings
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
from pyrogram.types import Photo


@sync_to_async
def insert_telegram_chat(chat, profile_file):
    channel_id = chat.id
    username = chat.username
    title = chat.title
    description = chat.description
    member_count = chat.members_count
    is_verified = chat.is_verified
    is_private = username is None

    try:
        # Insert or update the channel in the database
        return TelegramChat.objects.update_or_create(
            channel_id=channel_id,
            defaults={
                "username": username,
                "title": title,
                "description": description,
                "member_count": member_count,
                "is_verified": is_verified,
                "is_private": is_private,
                "profile_photo": profile_file,
            },
        )
    except Exception as e:
        print(f"Error updating channel: {str(e)}")
        return None


def get_max_photo_id(photo: Photo):
    """
    Get the file ID of the largest photo size.

    :param photo: Photo object from Pyrogram
    :return: File ID of the largest photo size
    """
    if not photo or not photo.sizes:
        return None  # No photo sizes available

    # Find the largest photo size based on width * height
    max_size = max(photo.sizes, key=lambda size: size.width * size.height)

    return max_size.file_id


async def chat_seeder():
    channels = settings.TELEGRAM_CHANNELS
    app = Client(
        "LaptopScraper",
        api_id=settings.TELEGRAM_API_ID,
        api_hash=settings.TELEGRAM_API_HASH,
        session_string=settings.TELEGRAM_SESSIONS,
    )
    async with app:
        for channel in channels:
            try:
                chat = await app.get_chat(int(channel))
                profile_photo_file = None
                if chat.photo:
                    try:
                        file_bytes = await app.download_media(
                            chat.photo.big_file_id, in_memory=True
                        )
                        file_bytes.seek(0)

                        # Create a unique filename for the photo
                        file_name = f"telegram_profile_{channel}.jpg"

                        # Save the file as a Django FileField

                        profile_photo_file = ContentFile(
                            file_bytes.read(), name=file_name
                        )
                    except Exception as e:
                        print(f"Error downloading photo: {str(e)}")
                inserted_data = await insert_telegram_chat(chat, profile_photo_file)
                print(inserted_data)
            except Exception as e:
                print("Error occured: ", e)
