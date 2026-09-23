from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BloodRequestViewSet

router = DefaultRouter()
router.register(r'', BloodRequestViewSet, basename='bloodrequest')

urlpatterns = [
    path('', include(router.urls)),
]
