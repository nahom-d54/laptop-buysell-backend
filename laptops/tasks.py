from pyrogram import Client
from django.conf import settings
from .models import LaptopPost
import re
import json
import google.generativeai as genai


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
            return False, f"Key '{key}' has invalid type. Expected {expected_type}, got {type(data[key])}"
        else:
            return False, f"Missing required key: {key}"

    return True, cleaned_data 




def get_json_response(data):
    pattern = r'\{[^{}]*\}'
    match = re.findall(pattern, data)
    return match[0] if match else {}


def process_product(product):
    
    response = model.generate_content(product)
    json_response = get_json_response(response.text)

    final_response = json.loads(json_response)

    status, verified_product = verify_laptop_dict(final_response)

    return status, verified_product

    

def scrape_laptops():
    app = Client(settings.TELEGRAM_SESSIONS, api_id=settings.TELEGRAM_API_ID, api_hash=settings.TELEGRAM_API_HASH)
    channels = settings.TELEGRAM_CHANNELS
    with app:
        for channel in channels:
            messages = app.get_chat_history(channel, limit=50)
            for message in messages:
                # customize based on the channel so i might need to make it dynamic
                status, processed_product = process_product(message)
                if status:
                    LaptopPost.objects.update_or_create(
                        channel_name=message.sender_chat,
                        posted_at=message.date,
                        post_id=message.id,
                        defaults=processed_product
                    )
