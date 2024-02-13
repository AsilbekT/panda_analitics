from rest_framework import serializers
from .models import ActivityType, BannerClick, BannerImpression, StreamingQualityData, UserSessionData, UserWatchData, UserActivity, Review, ContentType, Content

from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
      

class UserWatchDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWatchData
        fields = [
            'user_id', 'content_id', 'watch_duration', 'timestamp',
            'fully_watched', 'paused_count', 'rewind_count',
            'fast_forward_count', 'completed', 'content_type'
        ]


class UserActivitySerializer(serializers.ModelSerializer):

    class Meta:
        model = UserActivity

        fields = [
            'user_id', 'content_id', 'activity_type',
            'playback_position', 'timestamp', 'content_type'
        ]

class LikeUnlikeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    content_id = serializers.IntegerField()
    content_type = serializers.ChoiceField(choices=ContentType.choices)
    like = serializers.BooleanField(allow_null=True, required=False)  # Allows null for undo

    def validate_content_type(self, value):
        if value not in ContentType.values:
            raise serializers.ValidationError("Invalid content type.")
        return value

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['user_id', 'content_id',
                  'review_text', 'rating', 'sentiment_score']


class StreamingQualityDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamingQualityData
        fields = ['user_id', 'content_id',
                  'buffering_count', 'average_load_time']


class UserSessionDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSessionData
        fields = ['user_id', 'session_start', 'session_end']


class BannerClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerClick
        fields = ['banner_id', 'user_id', 'page_url', 'device_info']


class BannerImpressionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BannerImpression
        fields = ['banner_id', 'user_id']



class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__' 