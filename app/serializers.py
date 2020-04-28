from rest_framework import serializers
from app.models import User, Idea, Comment, SocialMediaDetails, UserFCMDevice

class SocialSerializer(serializers.Serializer):
    """
    Serializer which accepts an OAuth2 access token and provider.
    """
    provider = serializers.CharField(max_length=255, required=True)
    access_token = serializers.CharField(max_length=4096, required=True, trim_whitespace=True)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'platform', 'email', 'password')

class IdeaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Idea
        fields = "__all__"

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"

class SocialMediaDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaDetails
        fields = "__all__"

class UserFCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFCMDevice
        fields = "__all__"