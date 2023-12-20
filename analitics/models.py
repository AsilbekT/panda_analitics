from django.db import models


class ActivityType(models.TextChoices):
    WATCHED = 'watched', 'Watched'
    LIKED = 'liked', 'Liked'
    UNLIKED = 'unliked', 'Unliked'
    SHARED = 'shared', 'Shared'


class UserWatchData(models.Model):
    user_id = models.IntegerField()
    content_id = models.IntegerField()
    watch_duration = models.IntegerField(help_text="Duration in seconds")
    timestamp = models.DateTimeField(auto_now_add=True)
    fully_watched = models.BooleanField(default=False)
    paused_count = models.IntegerField(default=0)
    rewind_count = models.IntegerField(default=0)
    fast_forward_count = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"User {self.user_id} Watch Data for Content {self.content_id}"


class StreamingQualityData(models.Model):
    user_id = models.IntegerField()
    content_id = models.IntegerField()
    buffering_count = models.IntegerField(default=0)
    average_load_time = models.FloatField()

    def __str__(self):
        return f"Streaming Quality for User {self.user_id}, Content {self.content_id}"


class UserSessionData(models.Model):
    user_id = models.IntegerField()
    session_start = models.DateTimeField()
    session_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session Data for User {self.user_id}"


class UserActivity(models.Model):
    user_id = models.IntegerField()
    content_id = models.IntegerField()
    activity_type = models.CharField(
        max_length=100, choices=ActivityType.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    device_type = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    platform = models.CharField(max_length=100, blank=True, null=True)
    playback_position = models.IntegerField(
        help_text="Playback position in seconds", blank=True, null=True)
    content_type = models.CharField(max_length=100, choices=[
                                    ('movie', 'MOVIE'), ('series', 'SERIES')])

    def __str__(self):
        return f"User {self.user_id} - {self.activity_type} - Content {self.content_id}"


class UserAcquisitionData(models.Model):
    user_id = models.IntegerField()
    acquisition_source = models.CharField(max_length=100)
    registration_date = models.DateTimeField()

    def __str__(self):
        return f"Acquisition Data for User {self.user_id}"


class Review(models.Model):
    user_id = models.IntegerField()
    content_id = models.IntegerField()
    review_text = models.TextField()
    rating = models.IntegerField()  # Assuming a numerical rating
    timestamp = models.DateTimeField(auto_now_add=True)
    sentiment_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Review by User {self.user_id} for Content {self.content_id}"


class ContentRevenue(models.Model):
    content_id = models.IntegerField()
    subscription_plan_id = models.IntegerField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"Revenue for Content {self.content_id} - Date: {self.date}"


# models.py

class BannerClick(models.Model):
    banner_id = models.IntegerField()
    clicked_at = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField()  # Assuming you track users by an ID
    # Page where the banner was clicked
    page_url = models.URLField(blank=True, null=True)
    device_info = models.CharField(
        max_length=255, blank=True, null=True)  # Device information

    def __str__(self):
        return f"Click on Banner {self.banner_id} by User {self.user_id}"


class BannerImpression(models.Model):
    banner_id = models.IntegerField()
    viewed_at = models.DateTimeField(auto_now_add=True)
    user_id = models.IntegerField()  # Assuming you track users by an ID

    def __str__(self):
        return f"Impression on Banner {self.banner_id} by User {self.user_id}"
