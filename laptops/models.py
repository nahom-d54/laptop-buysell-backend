from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class LaptopPost(models.Model):
    title = models.CharField(max_length=255)

    storage = models.CharField(max_length=255, null=True, blank=True)
    processor = models.CharField(max_length=255, null=True, blank=True)
    graphics = models.CharField(max_length=255, null=True, blank=True)
    display = models.CharField(max_length=255, null=True, blank=True)
    ram = models.CharField(max_length=255, null=True, blank=True)
    battrey = models.CharField(max_length=255, null=True, blank=True)

    status = models.CharField(max_length=40, null=True, blank=True)

    color = models.CharField(max_length=20, null=True, blank=True)

    description = models.TextField(null=True, blank=True)
    price = models.CharField(max_length=50, null=True, blank=True)
    post_id = models.IntegerField(unique=True)
    channel_name = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=50, null=True)
    posted_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-posted_at"]

    def __str__(self):
        return self.title


class Review(models.Model):
    product = models.ForeignKey(
        LaptopPost, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()  # 1 to 5, for example
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"

    class Meta:
        unique_together = (
            "product",
            "user",
        )  # Prevent duplicate reviews by the same user for the same product
