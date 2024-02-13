# admin.py

from django.contrib import admin
from .models import BannerClick, BannerImpression, UserActivity, Review, UserWatchData, Content
from django.utils.text import slugify

@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'content_id', 'activity_type', 'timestamp')
    list_filter = ('activity_type', 'timestamp')
    search_fields = ('user_id', 'content_id')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'content_id', 'rating', 'timestamp')
    list_filter = ('rating', 'timestamp')
    search_fields = ('user_id', 'content_id')


@admin.register(UserWatchData)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'content_id', 'watch_duration', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user_id', 'content_id')


class BannerClickAdmin(admin.ModelAdmin):
    list_display = ('banner_id', 'clicked_at',
                    'user_id', 'page_url', 'device_info')
    list_filter = ('banner_id', 'clicked_at')
    search_fields = ('user_id',)


class BannerImpressionAdmin(admin.ModelAdmin):
    list_display = ('banner_id', 'viewed_at', 'user_id')
    list_filter = ('banner_id', 'viewed_at')
    search_fields = ('user_id',)

class ContentAdmin(admin.ModelAdmin):
    list_display = ('content_id', 'title', 'content_type', 'release_date', 'duration_minute')
    list_filter = ('content_type', 'release_date')
    search_fields = ('title', 'description', 'genre')
    ordering = ('release_date', 'content_id')
    fields = ('content_id', 'title', 'slug', 'description', 'genre', 'release_date', 'duration_minute', 'thumbnail_image', 'widescreen_thumbnail_image', 'content_type', 'series_id')
    readonly_fields = ('slug',)

    def save_model(self, request, obj, form, change):
        if not obj.slug:  # Generate slug if it's not provided
            obj.slug = slugify(obj.title)
        super().save_model(request, obj, form, change)

admin.site.register(Content, ContentAdmin)
admin.site.register(BannerClick, BannerClickAdmin)
admin.site.register(BannerImpression, BannerImpressionAdmin)
