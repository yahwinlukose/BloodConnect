from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceTokenViewSet

router = DefaultRouter()
router.register(r'tokens', DeviceTokenViewSet, basename='device-token')

urlpatterns = [
    path('', include(router.urls)),
]
