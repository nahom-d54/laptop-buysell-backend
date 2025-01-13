from rest_framework import serializers
from .models import LaptopPost, Review, LaptopImage, TelegramChat
from rest_framework.reverse import reverse


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "rating", "comment", "created_at"]


class LaptopImageSerializer(serializers.Serializer):
    image = serializers.ImageField()

    class Meta:
        model = LaptopImage
        fields = ["image", "post"]


class ChatSerializer(serializers.ModelSerializer):
    chat_posts = serializers.SerializerMethodField()

    class Meta:
        model = TelegramChat
        fields = "__all__"

    def get_chat_posts(self, obj):
        request = self.context.get("request")
        if request:
            # Build the base URL dynamically
            base_url = f"{request.scheme}://{request.get_host()}"
            return f"{base_url}/api/chat/{obj.channel_id}"
        # Fallback if no request is available
        return f"/api/chat/{obj.channel_id}"


class LaptopPostSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    images = LaptopImageSerializer(many=True, read_only=True)
    channel = serializers.SerializerMethodField()

    class Meta:
        model = LaptopPost
        exclude = ("channel_id", "channel_name")

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return 0

    def get_channel(self, obj):
        return reverse(
            "chat-detail",
            args=[obj.channel_id.channel_id],
            request=self.context.get("request"),
        )

    def to_representation(self, instance):
        # Call the parent method to get the initial representation
        representation = super().to_representation(instance)

        # Check if this is a single item retrieval
        if self.context.get("is_single_retrieval", False):
            # Keep `reviews` in the output
            return representation
        else:
            # Exclude `reviews` from the output
            representation.pop("reviews", None)
            return representation
