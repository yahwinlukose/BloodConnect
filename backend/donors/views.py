from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, NotFound
from .models import DonorProfile
from .serializers import DonorProfileSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class DonorProfileView(generics.RetrieveUpdateAPIView, generics.CreateAPIView):
    """
    API view for GET, POST, and PATCH on the authenticated user's DonorProfile.
    """
    serializer_class = DonorProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Overrides the default get_object to fetch the profile based on the authenticated user.
        Raises 404 if it does not exist.
        """
        try:
            return self.request.user.donor_profile
        except DonorProfile.DoesNotExist:
            raise NotFound(detail="Donor profile not found.")

    def post(self, request, *args, **kwargs):
        """
        Creates a new DonorProfile for the authenticated user.
        """
        if request.user.role != User.Role.DONOR:
            raise PermissionDenied(detail="Only users with the DONOR role can create a donor profile.")
            
        if hasattr(request.user, 'donor_profile'):
            return Response(
                {"detail": "User already has a donor profile."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Automatically sets the user field to the authenticated user upon creation.
        """
        serializer.save(user=self.request.user)
