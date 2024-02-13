from rest_framework import permissions

class IsAuthenticatedForGetOnly(permissions.BasePermission):
    """
    Custom permission to only allow authenticated users to make GET requests.
    """

    def has_permission(self, request, view):
        print(request.user)
        if request.method == 'GET':
            return request.user and request.user.is_authenticated
        return True  # Allow all non-GET requests
