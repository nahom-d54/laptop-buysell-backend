from rest_framework import serializers
from .models import LaptopPost, Review, LaptopImage


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


class LaptopPostSerializer(serializers.ModelSerializer):
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    images = LaptopImageSerializer(many=True, read_only=True)

    class Meta:
        model = LaptopPost
        fields = "__all__"

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews.exists():
            return sum(review.rating for review in reviews) / reviews.count()
        return 0

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
