from celery import shared_task
from .models import BannerClick, BannerImpression, Review, StreamingQualityData, UserActivity, UserSessionData, UserWatchData
from datetime import timedelta
from django.utils import timezone
from django.db import models


@shared_task
def save_watch_data(user_id, content_id, watch_duration, content_type):
    threshold_for_full_watch = 3600
    fully_watched = watch_duration >= threshold_for_full_watch

    # Check if the object exists
    print(content_type)
    obj, created = UserWatchData.objects.get_or_create(
        user_id=user_id,
        content_id=content_id,
        defaults={
            'watch_duration': watch_duration,
            'fully_watched': fully_watched,
            'content_type': content_type,
        }
    )

    if not created:
        obj.watch_duration = models.F('watch_duration') + watch_duration
        obj.fully_watched = fully_watched
        obj.content_type = content_type  # Explicitly update content_type
        obj.save()


@shared_task
def add_user_activity(user_id, content_id, activity_type, playback_position, content_type, watch_timestamp=None):

    obj, created = UserActivity.objects.get_or_create(
        user_id=user_id,
        content_id=content_id,
        defaults={
            'activity_type': activity_type,
            'playback_position': playback_position,
            'content_type': content_type,
        }
    )
    if not created:
        if watch_timestamp is not None:
            obj.watch_timestamp = watch_timestamp
            
        obj.playback_position = playback_position
        obj.activity_type = activity_type
        obj.content_type = content_type
        obj.save()

@shared_task
def add_review(user_id, content_id, review_text, rating):
    Review.objects.update_or_create(
        user_id=user_id,
        content_id=content_id,
        defaults={
            'review_text': review_text,
            'rating': rating
        }
    )


@shared_task
def process_streaming_quality_data(user_id, content_id, buffering_count, average_load_time):
    try:
        StreamingQualityData.objects.create(
            user_id=user_id,
            content_id=content_id,
            buffering_count=buffering_count,
            average_load_time=average_load_time
        )
    except Exception as e:
        # Handle exceptions (logging, retrying, etc.)
        pass


@shared_task
def process_user_session_data(user_id, session_start, session_end=None):
    # If session_end is not provided, it means the session has just started
    if session_end is None:
        session_end = session_start  # Initially, set session_end equal to session_start

    # Check if a session already exists for the given start time
    session, created = UserSessionData.objects.get_or_create(
        user_id=user_id,
        session_start=session_start,
        defaults={
            'session_end': session_end
        }
    )

    # If the session already exists and we have a session_end time, update it
    if not created and session_end:
        session.session_end = session_end
        session.save()


@shared_task
def save_banner_click(banner_id, user_id, page_url, device_info):
    BannerClick.objects.create(
        banner_id=banner_id,
        user_id=user_id,
        page_url=page_url,
        device_info=device_info
    )


@shared_task
def save_banner_impression(banner_id, user_id):
    BannerImpression.objects.create(
        banner_id=banner_id,
        user_id=user_id
    )
