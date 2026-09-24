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

class DonorMatchesView(generics.ListAPIView):
    """
    API view for a donor to list matches assigned to them for active blood requests.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        from matching.serializers import DonorMatchForDonorSerializer
        return DonorMatchForDonorSerializer

    def get_queryset(self):
        try:
            donor_profile = self.request.user.donor_profile
        except DonorProfile.DoesNotExist:
            raise PermissionDenied(detail="User does not have a donor profile.")

        from matching.models import DonorMatching
        from blood_requests.models import BloodRequest

        return DonorMatching.objects.filter(
            donor=donor_profile,
            blood_request__status__in=[BloodRequest.Status.PENDING, BloodRequest.Status.MATCHING]
        ).order_by('-created_at')

from rest_framework.views import APIView
from django.utils import timezone

class DonorMatchActionView(APIView):
    """
    Base view for accepting or rejecting a match.
    """
    permission_classes = [IsAuthenticated]
    action = None # 'ACCEPT' or 'REJECT'

    def post(self, request, match_id, *args, **kwargs):
        try:
            donor_profile = request.user.donor_profile
        except DonorProfile.DoesNotExist:
            raise PermissionDenied(detail="User does not have a donor profile.")

        from matching.models import DonorMatching

        try:
            match = DonorMatching.objects.get(id=match_id, donor=donor_profile)
        except DonorMatching.DoesNotExist:
            raise NotFound(detail="Match not found or does not belong to the authenticated donor.")

        if match.status not in [DonorMatching.Status.PENDING, DonorMatching.Status.NOTIFIED]:
            return Response(
                {"detail": f"Cannot transition from {match.status}."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if self.action == 'ACCEPT':
            match.status = DonorMatching.Status.ACCEPTED
        elif self.action == 'REJECT':
            match.status = DonorMatching.Status.REJECTED

        match.responded_at = timezone.now()
        match.save(update_fields=['status', 'responded_at'])

        from matching.serializers import DonorMatchForDonorSerializer
        serializer = DonorMatchForDonorSerializer(match)
        return Response(serializer.data)

class DonorMatchAcceptView(DonorMatchActionView):
    action = 'ACCEPT'

class DonorMatchRejectView(DonorMatchActionView):
    action = 'REJECT'
