from rest_framework.response import Response
from rest_framework import status


def standard_response(success, message, data=None, status_code=status.HTTP_200_OK):
    response_status = 'success' if success else 'error'
    return Response({
        'status': response_status,
        'message': message,
        'data': data if data is not None else []
    }, status=status_code)
