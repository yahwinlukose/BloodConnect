from django.urls import path
from .views import (
    DonorProfileView,
    DonorMatchesView,
    DonorMatchAcceptView,
    DonorMatchRejectView
)

urlpatterns = [
    path('profile/', DonorProfileView.as_view(), name='donor_profile'),
    path('matches/', DonorMatchesView.as_view(), name='donor_matches'),
    path('matches/<int:match_id>/accept/', DonorMatchAcceptView.as_view(), name='donor_match_accept'),
    path('matches/<int:match_id>/reject/', DonorMatchRejectView.as_view(), name='donor_match_reject'),
]
