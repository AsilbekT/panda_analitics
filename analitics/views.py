from rest_framework import status
from django.conf import settings
from analitics.pagination import StandardResultsSetPagination
from analitics.utils import standard_response
from .serializers import BannerClickSerializer, BannerImpressionSerializer, StreamingQualityDataSerializer, UserSessionDataSerializer, UserWatchDataSerializer, UserActivitySerializer, ReviewSerializer, UserSerializer
from .tasks import process_streaming_quality_data, process_user_session_data, save_banner_click, save_banner_impression, save_watch_data, add_user_activity, add_review
from django.db.models import Avg, Sum, Count, F, Case, When, FloatField
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ActivityType, BannerClick, BannerImpression, ContentRevenue, Review, UserActivity, UserSessionData, UserWatchData, ContentLikeUnlikeCount
import requests
from rest_framework.views import APIView
from django.db.models.functions import ExtractHour
from .serializers import LikeUnlikeSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .permissions import IsAuthenticatedForGetOnly
from .models import Content
from .serializers import ContentSerializer
from rest_framework import viewsets
import logging
from rest_framework.authentication import TokenAuthentication

# Set up logging
logger = logging.getLogger(__name__)

class UserWatchDataView(APIView):
    def post(self, request):
        serializer = UserWatchDataSerializer(data=request.data)
        if serializer.is_valid():
            valid_data = serializer.validated_data

            # Remove 'fully_watched' from valid_data if it exists
            user_id = valid_data.get('user_id', None)
            content_id = valid_data.get('content_id', None)
            watch_duration = valid_data.get('watch_duration', None)
            content_type = valid_data.get('content_type', None)
            print(content_type)
            # Call the Celery task with the correct data
            save_watch_data.delay(
                user_id=user_id, content_id=content_id, watch_duration=watch_duration, content_type=content_type)
            return standard_response(True, 'User watch data is being processed')
        return standard_response(False, 'Invalid data', serializer.errors, status.HTTP_400_BAD_REQUEST)




class UserActivityView(APIView):
    def post(self, request):
        serializer = UserActivitySerializer(data=request.data)
        if serializer.is_valid():
            # It looks like you forgot to assign serializer.validated_data to valid_data
            valid_data = serializer.validated_data
            print(valid_data)
            user_id = valid_data.get('user_id', None)
            content_id = valid_data.get('content_id', None)
            playback_position = valid_data.get('playback_position', None)
            content_type = valid_data.get('content_type', None)

            # Assuming add_user_activity is a Celery task
            add_user_activity.delay(**valid_data)

            return standard_response(True, 'User activity is being processed')
        else:
            # Log the serializer errors
            logger.error(f"Serializer Errors: {serializer.errors}")

            # Convert OrderedDict to a standard dict for better readability
            error_dict = dict(serializer.errors)

            return standard_response(False, 'Invalid data', error_dict, status.HTTP_400_BAD_REQUEST)


class ReviewView(APIView):
    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            add_review.delay(**serializer.validated_data)
            return standard_response(True, 'Review is being processed')
        return standard_response(False, 'Invalid data', serializer.errors, status.HTTP_400_BAD_REQUEST)


class MostWatchedContentView(APIView):
    def get(self, request):
        most_watched = UserWatchData.objects.values('content_id').annotate(
            watch_count=Count('id')
        ).order_by('-watch_count')[:10]

        return standard_response(True, 'Most watched content', {'most_watched': list(most_watched)})


class AverageSessionLengthView(APIView):
    def get(self, request):
        avg_session_length = UserWatchData.objects.aggregate(
            average_length=Avg('watch_duration')
        )

        return standard_response(True, 'Average session length', avg_session_length)


class PeakViewingTimesView(APIView):
    authentication_classes = [TokenAuthentication]

    permission_classes = [IsAuthenticatedForGetOnly]

    def get(self, request):
        peak_times = UserWatchData.objects.annotate(
            hour=ExtractHour('timestamp')
        ).values('hour').annotate(
            count=Count('id')
        ).order_by('-count')

        return standard_response(True, 'Peak viewing times', {'peak_times': list(peak_times)})


class TotalWatchDurationView(APIView):

    def get(self, request, content_id):
        total_duration = UserWatchData.objects.filter(content_id=content_id).aggregate(
            total_watch_duration=Sum('watch_duration'),
            watch_count=Count('id')
        )
        return standard_response(True, 'Total Watch Duration calculated', total_duration)


class TotalReviewsView(APIView):
    def get(self, request, content_id):
        reviews_stats = Review.objects.filter(content_id=content_id).aggregate(
            total_reviews=Count('id'),
            avg_rating=Avg('rating')
        )
        return standard_response(True, 'Average rating calculated', reviews_stats)


class UserTotalWatchStatisticsView(APIView):
    def get(self, request, user_id):
        total_watch_data = UserWatchData.objects.filter(user_id=user_id).aggregate(
            total_views=Count('id'),
            total_watch_time=Sum('watch_duration')
        )
        return standard_response(True, 'Total watch statistics retrieved', total_watch_data)


class ContentWatchCountView(APIView):
    
    def get(self, request, content_id):
        watch_counts = UserWatchData.objects.filter(
            content_id=content_id,
            fully_watched=True
        ).count()
        return standard_response(True, 'Content watch count retrieved', {'watch_count': watch_counts})


class LastWatchedPositionView(APIView):
    def get(self, request, user_id, content_id, content_type):

        last_activity = UserActivity.objects.filter(
            user_id=user_id,
            content_id=content_id,
            content_type=content_type,
            activity_type=ActivityType.WATCHED
        ).order_by('-timestamp').first()
        if last_activity:
            response_data = {
                'last_watched': last_activity.timestamp,
                'activity_type': last_activity.activity_type,
                'content_type':content_type,
                'playback_position': last_activity.playback_position
            }
            return standard_response(True, 'Last watched position retrieved', response_data)
        else:
            return standard_response(False, 'No activity found', [])


class StreamingQualityDataView(APIView):
    def post(self, request):
        serializer = StreamingQualityDataSerializer(data=request.data)
        if serializer.is_valid():
            # Send data to Celery task
            process_streaming_quality_data.delay(**serializer.validated_data)
            return standard_response(True, 'Streaming quality data is being processed')
        return standard_response(False, 'Invalid data', serializer.errors, status.HTTP_400_BAD_REQUEST)


class UserSessionDataView(APIView):
    def post(self, request):
        serializer = UserSessionDataSerializer(data=request.data)
        if serializer.is_valid():
            # Send data to Celery task
            process_user_session_data.delay(**serializer.validated_data)
            return standard_response(True, 'User session data is being processed')
        return standard_response(False, 'Invalid data', serializer.errors, status.HTTP_400_BAD_REQUEST)


class UserSessionHistoryView(APIView):
    def get(self, request, user_id):
        sessions = UserSessionData.objects.filter(
            user_id=user_id).order_by('-session_start')
        serializer = UserSessionDataSerializer(sessions, many=True)
        return Response(serializer.data)


# Billing data


class FetchTotalRevenueView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedForGetOnly]

    """
    Billing service
    Response:
        {
            "status": "success",
            "message": "Total revenue retrieved",
            "data": {
                "total_revenue": 4000.0,
                "daily_revenue": null,
                "weekly_revenue": null,
                "monthly_revenue": 4000.0
            }
        }
    """

    def get(self, request):
        response = requests.get(
            f"{settings.BILLING_SERVICE_URL}/total-revenue/")
        if response.status_code == 200:
            return standard_response(True, 'Total revenue retrieved', response.json()['data'])
        return standard_response(False, 'Failed to fetch data', status_code=response.status_code)


class FetchRevenueByPlanView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedForGetOnly]

    """
    Billing service
    Response:
        {
            "status": "success",
            "message": "Revenue by plan retrieved",
            "data": {
                "revenue_by_plan": [
                    {
                        "plan__name": "Basic",
                        "total_revenue": 3000.0,
                        "transaction_count": 3,
                        "average_revenue_per_plan": 1000.0
                    }
                ]
            }
        }
    """

    def get(self, request):
        response = requests.get(
            f"{settings.BILLING_SERVICE_URL}/revenue-by-plan/")
        if response.status_code == 200:
            return standard_response(True, 'Revenue by plan retrieved', response.json()['data'])
        return standard_response(False, 'Failed to fetch data', status_code=response.status_code)


class FetchARPUView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedForGetOnly]

    """
    Billing service
    Response:
        {
            "status": "success",
            "message": "Average Revenue Per User retrieved",
            "data": {
                "arpu": [
                    {
                        "user__username": "asadbek",
                        "total_revenue": 1000.0,
                        "average_revenue": 1000.0,
                        "transaction_count": 1
                    },
                    {
                        "user__username": "asilbek",
                        "total_revenue": 3000.0,
                        "average_revenue": 1000.0,
                        "transaction_count": 3
                    }
                ]
            }
        }
    """

    def get(self, request):
        response = requests.get(f"{settings.BILLING_SERVICE_URL}/arpu/")
        if response.status_code == 200:
            return standard_response(True, 'Average Revenue Per User retrieved', response.json()['data'])
        return standard_response(False, 'Failed to fetch data', status_code=response.status_code)


class FetchTransactionRatesView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedForGetOnly]

    """
    Billing service
    Response:
        {
            "status": "success",
            "message": "Transaction rates retrieved",
            "data": {
                "success_rate": 100.0,
                "failure_rate": 0.0,
                "status_counts": [
                    {
                        "status": "Completed",
                        "count": 4
                    }
                ]
            }
        }
    """

    def get(self, request):
        response = requests.get(
            f"{settings.BILLING_SERVICE_URL}/transaction-rates/")
        if response.status_code == 200:
            return standard_response(True, 'Transaction rates retrieved', response.json()['data'])
        return standard_response(False, 'Failed to fetch data', status_code=response.status_code)


class UserStatisticsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedForGetOnly]


    """
    Fetches user-related statistics from the user service.
    """

    def get(self, request):
        # URL of the user service endpoint for statistics
        # Replace with the actual URL
        user_service_statistics_url = settings.USER_SERVICE_URL + 'statistics'

        try:
            response = requests.get(user_service_statistics_url)
            if response.status_code == 200:
                # Successfully retrieved data
                return standard_response(True, 'User statistics retrieved successfully', response.json()['data'])
            else:
                # Handle error cases
                return standard_response(False, 'Failed to retrieve user statistics', status_code=response.status_code)
        except requests.RequestException as e:
            # Handle exceptions like connection errors
            return standard_response(False, f'Error fetching user statistics: {str(e)}')


class BannerView(APIView):
    def post(self, request):
        action_type = request.data.get('action_type')

        if action_type == 'click':
            serializer = BannerClickSerializer(data=request.data)
            if serializer.is_valid():
                # Extract validated data and provide default values
                validated_data = serializer.validated_data
                page_url = validated_data.get('page_url', '')
                device_info = validated_data.get('device_info', '')

                # Pass data with defaults to the Celery task
                save_banner_click.delay(
                    banner_id=validated_data['banner_id'],
                    user_id=validated_data['user_id'],
                    page_url=page_url,
                    device_info=device_info
                )
                return Response({'status': 'Banner click being processed'}, status=202)

        elif action_type == 'view':
            serializer = BannerImpressionSerializer(data=request.data)
            if serializer.is_valid():
                save_banner_impression.delay(**serializer.validated_data)
                return Response({'status': 'Banner impression being processed'}, status=202)

        return Response({'error': 'Invalid action type or data'}, status=400)

    def get(self, request):
        # Aggregating Click Data
        click_data = BannerClick.objects.values('banner_id').annotate(
            total_clicks=Count('id'),
            unique_user_clicks=Count('user_id', distinct=True),
        ).order_by('banner_id')

        # Aggregating Impression Data
        impression_data = BannerImpression.objects.values('banner_id').annotate(
            total_impressions=Count('id')
        ).order_by('banner_id')

        # Convert QuerySets to lists for easier processing
        click_list = list(click_data)
        impression_list = list(impression_data)

        # Combine data in Python
        combined_statistics = {}
        for click in click_list:
            banner_id = click['banner_id']
            total_clicks = click['total_clicks']
            total_impressions = 0
            impression = next(
                (imp for imp in impression_list if imp['banner_id'] == banner_id), None)

            if impression:
                total_impressions = impression['total_impressions']

            # Debugging: Log the intermediate values
            print(
                f"Banner ID: {banner_id}, Clicks: {total_clicks}, Impressions: {total_impressions}")

            # Calculate CTR, avoiding division by zero
            ctr = (total_clicks / total_impressions *
                   100) if total_impressions > 0 else 0

            combined_statistics[banner_id] = {
                'total_clicks': total_clicks,
                'unique_user_clicks': click['unique_user_clicks'],
                'total_impressions': total_impressions,
                'click_through_rate': ctr
            }

        return Response({'banner_statistics': combined_statistics})


class UserWatchHistoryView(APIView):
    def get(self, request, user_id):
        watch_history = UserWatchData.objects.filter(user_id=user_id).order_by('-timestamp')
        # user_activity = UserActivity.objects.filter(user_id=user_id).order_by('-timestamp')
        # Instantiate your pagination class
        paginator = StandardResultsSetPagination()

        # Get the paginated queryset
        page = paginator.paginate_queryset(watch_history, request)

        def generate_content_url(content, series_id=None):
            base_url = "https://gateway.pandatv.uz/catalogservice"
            if content.content_type.lower() == 'movie':
                return f"{base_url}/movies/{content.content_id}/"
            elif content.content_type.lower() == 'episode':
                return f"{base_url}/series/{series_id}/"
            else:
                return None

        def process_watch_data(watch_data):
            # Fetch content details only for the corresponding content_id and content_type
            contents_query = Content.objects.filter(
                content_id=watch_data.content_id, 
                content_type=watch_data.content_type
            )


            if not contents_query.exists():
                # If content does not exist, skip this watch data
                return None

            content = contents_query.first()
            content_data = ContentSerializer(content).data
            watch_data_data = UserWatchDataSerializer(watch_data).data
            watch_data_data['content_details'] = content_data

            if content_data:
                if 'genre' in content_data:
                    content_data['genre'] = content_data['genre'].split(',')

                last_activity = UserActivity.objects.filter(
                    user_id=user_id,
                    content_id=watch_data.content_id,
                    content_type=watch_data.content_type,
                    activity_type=ActivityType.WATCHED
                ).order_by('-timestamp').first()

                last_watched_position = last_activity.playback_position if last_activity else None
                watch_data_data['last_watched_position'] = last_watched_position

                if content_data.get('series_id') != 0:
                    watch_data_data['content_url'] = generate_content_url(watch_data, content_data['series_id'])
                else:
                    watch_data_data['content_url'] = generate_content_url(watch_data)

                return watch_data_data

        def filter_none_values(data_list):
            return [data for data in data_list if data is not None]

        if page is not None:
            combined_data = filter_none_values([process_watch_data(watch_data) for watch_data in page])
            return paginator.get_paginated_response(combined_data)

        combined_data = filter_none_values([process_watch_data(watch_data) for watch_data in watch_history])
        return Response(combined_data)


class LikeUnlikeContentView(APIView):
    def post(self, request):
        serializer = LikeUnlikeSerializer(data=request.data)
        if serializer.is_valid():
            user_id = serializer.validated_data['user_id']
            content_id = serializer.validated_data['content_id']
            content_type = serializer.validated_data['content_type']
            like = serializer.validated_data.get('like')

            if like is None:  # Undo action
                self._undo_like_unlike(user_id, content_id, content_type)
                return standard_response(True, 'Like/Unlike action undone')
            else:
                self._process_like_unlike(user_id, content_id, content_type, like)
                return standard_response(True, 'User activity updated')

        return Response(serializer.errors, status=400)
        
    def _undo_like_unlike(self, user_id, content_id, content_type):
        # Remove the user's activity and update count
        activity = UserActivity.objects.filter(
            user_id=user_id, content_id=content_id, content_type=content_type
        ).first()

        if not activity:
            return

        content_like_unlike = ContentLikeUnlikeCount.objects.get(
            content_id=content_id, content_type=content_type
        )

        # Update the like or unlike count based on previous activity
        if activity.activity_type == ActivityType.LIKED:
            content_like_unlike.like_count = F('like_count') - 1
        elif activity.activity_type == ActivityType.UNLIKED:
            content_like_unlike.unlike_count = F('unlike_count') - 1

        content_like_unlike.save()
        activity.delete()

    def _process_like_unlike(self, user_id, content_id, content_type, like):
        activity_type = ActivityType.LIKED if like else ActivityType.UNLIKED

        # Update UserActivity
        UserActivity.objects.update_or_create(
            user_id=user_id,
            content_id=content_id,
            content_type=content_type,
            defaults={
                'activity_type': activity_type
            }
        )

        # Update ContentLikeUnlikeCount
        content_like_unlike, _ = ContentLikeUnlikeCount.objects.get_or_create(
            content_id=content_id,
            content_type=content_type
        )
        if like:
            content_like_unlike.like_count = F('like_count') + 1
        else:
            content_like_unlike.unlike_count = F('unlike_count') + 1

        content_like_unlike.save()


class ContentLikesCountView(APIView):
    
    def get(self, request, content_id, content_type):
        try:
            like_unlike_count = ContentLikeUnlikeCount.objects.get(
                content_id=content_id, 
                content_type=content_type
            )
            data = {
                'likes_count': like_unlike_count.like_count,
                'unlikes_count': like_unlike_count.unlike_count
            }
            return standard_response(True, 'Likes and unlikes count retrieved', data)
        except ContentLikeUnlikeCount.DoesNotExist:
            # Handle the case where there is no record for the given content
            return standard_response(False, 'Content not found', {})



class ObtainAuthToken(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            user_data = UserSerializer(user).data
            return Response({'token': token.key, 'user': user_data})
        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)



class ContentSyncView(APIView):
    def post(self, request):
        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, content_id):
        print("here")
        try:
            content = AnalyticsContent.objects.get(id=content_id)
        except AnalyticsContent.DoesNotExist:
            return Response({'error': 'Content not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ContentSerializer(content, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContentDetail(APIView):
    """
    Retrieve, update or delete a content instance.
    """
    def get_object(self, pk):
        try:
            return Content.objects.get(content_id=pk)
        except Content.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        content = self.get_object(pk)
        if not content:
            return Response({'error': 'Content not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContentSerializer(content)
        return Response(serializer.data)

    def put(self, request, pk):
        content = self.get_object(pk)
        if not content:
            return Response({'error': 'Content not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ContentSerializer(content, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        content = self.get_object(pk)
        if not content:
            return Response({'error': 'Content not found'}, status=status.HTTP_404_NOT_FOUND)
        content.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)