from django.db import transaction
from django.db.models import F
from matching.models import DonorMatching
from matching.services import find_eligible_donors

"""
This module provides the orchestration layer for the donor matching process.
The matching engine determines candidate eligibility based on blood compatibility and rules.
This orchestration layer persists those candidate matches to the database.

NOTE: This layer does not establish medical eligibility or clinical suitability.
Final blood-bank/medical verification remains necessary.
"""

@transaction.atomic
def generate_matches(blood_request):
    """
    Generates and persists DonorMatching records for a given BloodRequest.
    Returns an ordered QuerySet of the matching records.
    """
    if not blood_request:
        return DonorMatching.objects.none()

    candidates = find_eligible_donors(blood_request)
    
    from decimal import Decimal
    
    for candidate in candidates:
        donor = candidate['donor']
        distance_km = candidate['distance_km']
        if distance_km is not None:
            # Ensure it passes the max_digits/decimal_places validators by converting via string
            distance_km = Decimal(str(round(distance_km, 2)))
        match_score = candidate['score']
        
        match, created = DonorMatching.objects.get_or_create(
            blood_request=blood_request,
            donor=donor,
            defaults={
                'distance_km': distance_km,
                'match_score': match_score,
                'status': DonorMatching.Status.PENDING,
            }
        )
        
        if not created and match.status == DonorMatching.Status.PENDING:
            update_fields = []
            if match.distance_km != distance_km:
                match.distance_km = distance_km
                update_fields.append('distance_km')
            if match.match_score != match_score:
                match.match_score = match_score
                update_fields.append('match_score')
                
            if update_fields:
                match.save(update_fields=update_fields)

    return DonorMatching.objects.filter(blood_request=blood_request).order_by(
        F('match_score').desc(),
        F('distance_km').asc(nulls_last=True)
    )
