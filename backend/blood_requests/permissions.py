from rest_framework import permissions
from django.contrib.auth import get_user_model

User = get_user_model()

class BloodRequestPermission(permissions.BasePermission):
    """
    Custom permission for BloodRequest API:
    - DONOR: Can view (safe methods). Cannot create/modify/delete.
    - REQUESTER: Can view. Can create. Can modify only their own requests.
    - ADMIN: Full access.
    """

    def has_permission(self, request, view):
        # All authenticated users can view
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Only REQUESTER and ADMIN can create (POST)
        if request.method == 'POST':
            return request.user and request.user.is_authenticated and request.user.role in [User.Role.REQUESTER, User.Role.ADMIN]

        # For object-level methods (PATCH, DELETE), we return True here 
        # and let has_object_permission handle the specific checks.
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # All authenticated users can view the object
        if request.method in permissions.SAFE_METHODS:
            return True

        # ADMIN has full access to any object
        if request.user.role == User.Role.ADMIN:
            return True

        # REQUESTER can only modify (PATCH/PUT) their own request
        if request.method in ['PUT', 'PATCH']:
            return obj.requester == request.user and request.user.role == User.Role.REQUESTER

        # Deletion is reserved for ADMIN only (normal users should cancel)
        if request.method == 'DELETE':
            return False

        return False
