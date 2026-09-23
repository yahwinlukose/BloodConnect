import math
import datetime
from donors.models import DonorProfile
from blood_requests.models import BloodRequest

"""
NOTE: The matching result is a preliminary application-level candidate match. 
Final donor eligibility, blood compatibility, crossmatching, and clinical suitability 
must be confirmed by qualified medical/blood-bank personnel.
"""

COMPATIBILITY_MAP = {
    'O-': ['O-'],
    'O+': ['O-', 'O+'],
    'A-': ['O-', 'A-'],
    'A+': ['O-', 'O+', 'A-', 'A+'],
    'B-': ['O-', 'B-'],
    'B+': ['O-', 'O+', 'B-', 'B+'],
    'AB-': ['O-', 'A-', 'B-', 'AB-'],
    'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+']
}

def calculate_distance_km(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a)) 
    r = 6371 # Radius of earth in kilometers
    return round(r * c, 2)

def find_eligible_donors(blood_request):
    """
    Find eligible donors for a given BloodRequest.
    Returns a list of dictionaries containing 'donor', 'distance_km', and 'score'.
    Sorted by score (descending), then distance_km (ascending).
    """
    if not blood_request:
        return []

    recipient_bg = blood_request.blood_group
    compatible_donor_bgs = COMPATIBILITY_MAP.get(recipient_bg, [])

    # Find available donors with compatible blood group and valid DOB
    donors = DonorProfile.objects.filter(
        is_available=True,
        blood_group__in=compatible_donor_bgs,
        date_of_birth__isnull=False
    )

    today = datetime.date.today()
    cutoff_date = today - datetime.timedelta(days=90)
    
    results = []

    for donor in donors:
        # Application-level eligibility check (90 days since last donation)
        if donor.last_donation_date and donor.last_donation_date > cutoff_date:
            continue

        # Calculate distance if both request and donor have coordinates
        distance_km = None
        if donor.latitude is not None and donor.longitude is not None and \
           blood_request.latitude is not None and blood_request.longitude is not None:
            distance_km = calculate_distance_km(
                float(blood_request.latitude), float(blood_request.longitude),
                float(donor.latitude), float(donor.longitude)
            )

        # Base scoring
        score = 50
        if distance_km is not None:
            if distance_km <= 5:
                score = 100
            elif distance_km <= 10:
                score = 90
            elif distance_km <= 20:
                score = 75
            elif distance_km <= 50:
                score = 50
            else:
                score = 25

        # Urgency adjustment
        if blood_request.urgency == BloodRequest.Urgency.URGENT:
            score += 5
        elif blood_request.urgency == BloodRequest.Urgency.CRITICAL:
            score += 10

        # Cap score at 100
        if score > 100:
            score = 100

        results.append({
            'donor': donor,
            'distance_km': distance_km,
            'score': score
        })

    # Sort results
    def sort_key(item):
        d = item['distance_km']
        d_val = d if d is not None else float('inf')
        return (-item['score'], d_val)

    results.sort(key=sort_key)
    return results
