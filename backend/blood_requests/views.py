from rest_framework import viewsets
from .models import BloodRequest
from .serializers import BloodRequestSerializer
from .permissions import BloodRequestPermission

class BloodRequestViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows blood requests to be viewed, created, edited, and cancelled.
    """
    serializer_class = BloodRequestSerializer
    permission_classes = [BloodRequestPermission]
    
    def get_queryset(self):
        return BloodRequest.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(requester=self.request.user)
