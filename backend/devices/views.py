from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import DeviceToken
from .serializers import DeviceTokenSerializer

class DeviceTokenViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows device tokens to be viewed, registered, or deactivated.
    """
    serializer_class = DeviceTokenSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def get_queryset(self):
        """
        Return only active tokens for the current authenticated user.
        """
        return DeviceToken.objects.filter(user=self.request.user, is_active=True)

    def create(self, request, *args, **kwargs):
        """
        Register a new device token or reactivate an existing one.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        device_type = serializer.validated_data.get('device_type', DeviceToken.DeviceType.ANDROID)
        
        # Check if the token already exists (for any user)
        # We need to enforce that the same token doesn't get assigned to multiple users 
        # simultaneously if it's the exact same physical device.
        try:
            device_token = DeviceToken.objects.get(token=token)
            
            # If the token exists but belongs to someone else, 
            # we should reassign it to the new user who just logged in on that device
            if device_token.user != request.user:
                device_token.user = request.user
            
            # Reactivate and update
            device_token.is_active = True
            device_token.device_type = device_type
            device_token.save()
            
            response_status = status.HTTP_200_OK
            
        except DeviceToken.DoesNotExist:
            # Create a new token
            device_token = DeviceToken.objects.create(
                user=request.user,
                token=token,
                device_type=device_type,
                is_active=True
            )
            response_status = status.HTTP_201_CREATED
            
        return Response(
            self.get_serializer(device_token).data,
            status=response_status
        )

    def perform_destroy(self, instance):
        """
        Deactivate the token instead of hard deleting it.
        """
        instance.is_active = False
        instance.save()
