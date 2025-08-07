from django.contrib import admin
from laptops.models import TelegramChat, LaptopPost, SimilarityScore, MentionTracker


@admin.register(MentionTracker)
class MentionTrackerAdmin(admin.ModelAdmin):
    list_display = [
        'channel', 'message_id', 'unread_count', 'is_processed', 
        'is_read', 'created_at', 'processed_at'
    ]
    list_filter = ['is_processed', 'is_read', 'channel', 'created_at']
    search_fields = ['mention_text', 'channel__title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


# Register your models here.
admin.site.register([TelegramChat, LaptopPost, SimilarityScore])
