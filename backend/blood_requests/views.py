from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from .models import BloodRequest
from .serializers import BloodRequestSerializer
from .permissions import BloodRequestPermission

User = get_user_model()

class BloodRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows blood requests to be viewed, created, edited, and cancelled.
    """
    serializer_class = BloodRequestSerializer
    permission_classes = [BloodRequestPermission]
    
    def get_queryset(self):
        user = self.request.user
        qs = BloodRequest.objects.all().order_by('-created_at')
        if self.action == 'list' and user.role not in [User.Role.ADMIN, User.Role.HOSPITAL, User.Role.BLOOD_BANK]:
            return qs.filter(requester=user)
        return qs

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)
        
    def _check_match_permission(self, blood_request):
        user = self.request.user
        if user.role == User.Role.ADMIN or user.role == User.Role.HOSPITAL or user.role == User.Role.BLOOD_BANK:
            return True
        if blood_request.requester != user:
            raise PermissionDenied("You do not have permission to access these matches.")
        return True

    @action(detail=True, methods=['post'], url_path='matches/generate')
    def generate_matches_action(self, request, pk=None):
        blood_request = self.get_object()
        self._check_match_permission(blood_request)
        
        from matching.orchestrator import generate_matches
        from matching.serializers import DonorMatchingSerializer
        
        matches = generate_matches(blood_request)
        serializer = DonorMatchingSerializer(matches, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='matches')
    def list_matches(self, request, pk=None):
        blood_request = self.get_object()
        self._check_match_permission(blood_request)
        
        from matching.models import DonorMatching
        from matching.serializers import DonorMatchingSerializer
        
        matches = DonorMatching.objects.filter(blood_request=blood_request).order_by(
            '-match_score', 'distance_km'
        )
        serializer = DonorMatchingSerializer(matches, many=True)
        return Response(serializer.data)
