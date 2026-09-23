from django.urls import path
from .views import DonorProfileView

urlpatterns = [
    path('profile/', DonorProfileView.as_view(), name='donor_profile'),
]
