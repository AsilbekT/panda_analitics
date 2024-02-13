from django.urls import path
from .views import (
    AverageSessionLengthView,
    BannerView,
    ContentLikesCountView,
    LikeUnlikeContentView,
    MostWatchedContentView,
    PeakViewingTimesView,
    StreamingQualityDataView,
    UserSessionDataView,
    UserStatisticsView,
    UserWatchDataView,
    UserActivityView,
    ReviewView,
    TotalWatchDurationView,
    TotalReviewsView,
    UserTotalWatchStatisticsView,
    ContentWatchCountView,
    LastWatchedPositionView,
    FetchTotalRevenueView,
    FetchRevenueByPlanView,
    FetchARPUView,
    FetchTransactionRatesView,
    UserWatchHistoryView,
    ObtainAuthToken,
    ContentSyncView,
    ContentDetail
)

urlpatterns = [
    path('user-watch-data/', UserWatchDataView.as_view(), name='user_watch_data'),
    path('user-activity/', UserActivityView.as_view(), name='user_activity'),
    path('review/', ReviewView.as_view(), name='review'),

    path('content-likes-count/<int:content_id>/<content_type>/',
         ContentLikesCountView.as_view(), name='content-likes-count'),
    path('most-watched/', MostWatchedContentView.as_view(),
         name='most_watched_content'),
    path('average-session-length/', AverageSessionLengthView.as_view(),
         name='average_session_length'),
    path('peak-viewing-times/', PeakViewingTimesView.as_view(),
         name='peak_viewing_times'),
    path('total-watch-duration/<int:content_id>/',
         TotalWatchDurationView.as_view(), name='total_watch_duration'),
    path('total-reviews/<int:content_id>/',
         TotalReviewsView.as_view(), name='total_reviews'),
    path('user-total-watch-statistics/<int:user_id>/',
         UserTotalWatchStatisticsView.as_view(), name='user_total_watch_statistics'),
    path('content-watch-count/<int:content_id>/',
         ContentWatchCountView.as_view(), name='content_watch_count'),
    path('last-watched-position/<int:user_id>/<int:content_id>/<str:content_type>/',
         LastWatchedPositionView.as_view(), name='last_watched_position'),
    path('user-watch-history/<int:user_id>/',
         UserWatchHistoryView.as_view(), name='user-watch-history'),
    path('streaming-quality-data/', StreamingQualityDataView.as_view(),
         name='streaming_quality_data'),
    path('user-session-data/', UserSessionDataView.as_view(),
         name='user_session_data'),
    path('fetch-total-revenue/', FetchTotalRevenueView.as_view(),
         name='fetch_total_revenue'),
    path('fetch-revenue-by-plan/', FetchRevenueByPlanView.as_view(),
         name='fetch_revenue_by_plan'),
    path('fetch-arpu/', FetchARPUView.as_view(), name='fetch_arpu'),
    path('fetch-transaction-rates/', FetchTransactionRatesView.as_view(),
         name='fetch_transaction_rates'),

    #  USER SERVICE
    path('all-users-statistics/',
         UserStatisticsView.as_view(), name='user-statistics'),
    path('banners/', BannerView.as_view(), name='banners'),
    path('like-unlike-content/', LikeUnlikeContentView.as_view(),
         name='like-unlike-content'),
     path('login/', ObtainAuthToken.as_view()),
    path('contents/', ContentSyncView.as_view(), name='content-list'),
    path('contents/<int:pk>/', ContentDetail.as_view(), name='content-detail'),
]
