from rest_framework import viewsets
from django.contrib.auth import get_user_model
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
