import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DonorProfile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=DonorProfile)
def run_matching_on_donor_profile_save(sender, instance, created, **kwargs):
    """
    When a DonorProfile is created or updated, regenerate matches for all
    active BloodRequests so that donors who register (or update eligibility)
    after a request already exists are included in matching.

    generate_matches() is idempotent:
      - It uses get_or_create, so no duplicate DonorMatching rows are produced.
      - It only updates distance_km / match_score on PENDING rows; it never
        changes ACCEPTED, REJECTED, CANCELLED, NOTIFIED, or EXPIRED statuses.

    Only PENDING and MATCHING requests are processed – the same statuses that
    DonorMatchesView exposes to donors.
    """
    try:
        from blood_requests.models import BloodRequest
        from matching.orchestrator import generate_matches

        active_statuses = [BloodRequest.Status.PENDING, BloodRequest.Status.MATCHING]
        active_requests = BloodRequest.objects.filter(status__in=active_statuses)

        for blood_request in active_requests:
            generate_matches(blood_request)

    except Exception:
        # Matching failure must never prevent the profile from being saved.
        logger.exception(
            "Retroactive matching failed after DonorProfile save (donor_id=%s).",
            instance.pk,
        )
