from rest_framework import serializers
from .models import Tag, User, TodoItem


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        # exclude = ["password"]


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data.get("username"),
            password=validated_data.get("password"),
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class TodoItemSerializer(serializers.ModelSerializer):
    # required=False -----> IMPORTANT!!, otherwise code=400
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = TodoItem
        fields = "__all__"
        read_only_fields = ["timestamp"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["tags"] = [
            tag["title"] for tag in TagSerializer(instance.tags.all(), many=True).data
        ]
        return representation
