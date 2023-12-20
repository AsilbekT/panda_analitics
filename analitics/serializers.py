from rest_framework import serializers
from .models import ActivityType, BannerClick, BannerImpression, StreamingQualityData, UserSessionData, UserWatchData, UserActivity, Review


class UserWatchDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserWatchData
        fields = [
            'user_id', 'content_id', 'watch_duration', 'timestamp',
            'fully_watched', 'paused_count', 'rewind_count',
            'fast_forward_count', 'completed'
        ]


class UserActivitySerializer(serializers.ModelSerializer):
    activity_type = serializers.ChoiceField(choices=ActivityType.choices)
    device_type = serializers.CharField(max_length=100)
    location = serializers.CharField(max_length=100)

    class Meta:
        model = UserActivity

        fields = [
            'user_id', 'content_id', 'activity_type',
            'playback_position', 'timestamp',
            'device_type', 'location'
        ]


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
