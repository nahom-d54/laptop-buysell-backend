from django.db import models


class LaptopPost(models.Model):
    title = models.CharField(max_length=255)

    storage = models.CharField(max_length=255)
    processor = models.CharField(max_length=255)
    graphics = models.CharField(max_length=255)
    display = models.CharField(max_length=255)
    ram = models.CharField(max_length=255)
    battrey = models.CharField(max_length=255)

    status = models.CharField(max_length=40)

    color = models.CharField(max_length=20)


    description = models.TextField()
    price = models.CharField(max_length=50, null=True, blank=True)
    post_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    channel_name = models.CharField(max_length=255, null=True, blank=True)
    posted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
