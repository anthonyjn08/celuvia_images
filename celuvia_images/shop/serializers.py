from rest_framework import serializers
from .models import Store, Category, Product, Size, Review


class StoreSerializer(serializers.ModelSerializer):
    """
    Sserializer class for the Store model.
    """
    class Meta:
        model = Store
        fields = [
            "id", "owner", "name", "description", "email",
            "phone_number", "is_active",
        ]


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer class for the Category model.
    """
    class Meta:
        model = Category
        fields = [
            "name", "slug",
        ]


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Product model.
    """
    class Meta:
        model = Product
        fields = [
            "store", "category", "name", "description",
            "image", "created_at", "is_active"
        ]


class SizeSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Size model.
    """
    class Meta:
        model = Size
        fields = [
            "product", "small_price", "medium_price", "large_price",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Review model.
    """
    class Meta:
        model = Review
        fields = [
            "product", "user", "rating",
            "comment", "verified", "created_at",
        ]
