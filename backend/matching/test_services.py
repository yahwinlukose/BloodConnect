from django.test import TestCase
from django.contrib.auth import get_user_model
from donors.models import DonorProfile
from blood_requests.models import BloodRequest
from matching.services import find_eligible_donors, calculate_distance_km
import datetime
import math

User = get_user_model()

class MatchingServiceTests(TestCase):
    def setUp(self):
        self.requester_user = User.objects.create_user(
            email='req@example.com', password='pwd', role=User.Role.USER
        )
        self.today = datetime.date.today()
        
        # Base request template
        self.base_request = {
            'requester': self.requester_user,
            'units_required': 1,
            'hospital_name': 'Test Hospital',
            'location': 'Test Location',
            'required_date': self.today + datetime.timedelta(days=1),
            'urgency': BloodRequest.Urgency.NORMAL
        }

    def _create_donor(self, email, blood_group, is_available=True, last_donation=None, lat=None, lon=None):
        u = User.objects.create_user(email=email, password='pwd', role=User.Role.USER)
        d = DonorProfile.objects.create(
            user=u,
            blood_group=blood_group,
            date_of_birth=datetime.date(1990, 1, 1),
            gender=DonorProfile.Gender.MALE,
            is_available=is_available,
            last_donation_date=last_donation,
            latitude=lat,
            longitude=lon
        )
        return d

    def _create_request(self, blood_group, urgency=BloodRequest.Urgency.NORMAL, lat=None, lon=None):
        data = self.base_request.copy()
        data['blood_group'] = blood_group
        data['urgency'] = urgency
        data['latitude'] = lat
        data['longitude'] = lon
        return BloodRequest.objects.create(**data)

    # BLOOD COMPATIBILITY TESTS
    def test_o_neg_request_accepts_only_o_neg(self):
        req = self._create_request('O-')
        d_oneg = self._create_donor('d1@e.com', 'O-')
        d_opos = self._create_donor('d2@e.com', 'O+')
        d_aneg = self._create_donor('d3@e.com', 'A-')
        
        results = find_eligible_donors(req)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['donor'], d_oneg)

    def test_o_pos_request_accepts_o_neg_and_o_pos(self):
        req = self._create_request('O+')
        d_oneg = self._create_donor('d1@e.com', 'O-')
        d_opos = self._create_donor('d2@e.com', 'O+')
        d_aneg = self._create_donor('d3@e.com', 'A-')
        
        results = find_eligible_donors(req)
        self.assertEqual(len(results), 2)
        donors = [r['donor'] for r in results]
        self.assertIn(d_oneg, donors)
        self.assertIn(d_opos, donors)
        self.assertNotIn(d_aneg, donors)

    def test_a_pos_request_accepts_a_pos_a_neg_o_pos_o_neg(self):
        req = self._create_request('A+')
        d_apos = self._create_donor('d1@e.com', 'A+')
        d_aneg = self._create_donor('d2@e.com', 'A-')
        d_opos = self._create_donor('d3@e.com', 'O+')
        d_oneg = self._create_donor('d4@e.com', 'O-')
        d_bpos = self._create_donor('d5@e.com', 'B+')
        
        results = find_eligible_donors(req)
        self.assertEqual(len(results), 4)
        donors = [r['donor'] for r in results]
        self.assertNotIn(d_bpos, donors)

    def test_a_neg_request_accepts_a_neg_and_o_neg(self):
        req = self._create_request('A-')
        d_aneg = self._create_donor('d1@e.com', 'A-')
        d_oneg = self._create_donor('d2@e.com', 'O-')
        d_apos = self._create_donor('d3@e.com', 'A+')
        
        results = find_eligible_donors(req)
        self.assertEqual(len(results), 2)

    def test_b_pos_request_accepts_b_pos_b_neg_o_pos_o_neg(self):
        req = self._create_request('B+')
        d_bpos = self._create_donor('d1@e.com', 'B+')
        d_bneg = self._create_donor('d2@e.com', 'B-')
        d_opos = self._create_donor('d3@e.com', 'O+')
        d_oneg = self._create_donor('d4@e.com', 'O-')
        d_apos = self._create_donor('d5@e.com', 'A+')
        
        results = find_eligible_donors(req)
        self.assertEqual(len(results), 4)
        donors = [r['donor'] for r in results]
        self.assertNotIn(d_apos, donors)

    def test_b_neg_request_accepts_b_neg_and_o_neg(self):
        req = self._create_request('B-')
        d_bneg = self._create_donor('d1@e.com', 'B-')
        d_oneg = self._create_donor('d2@e.com', 'O-')
        d_opos = self._create_donor('d3@e.com', 'O+')
        
        results = find_eligible_donors(req)
        self.assertEqual(len(results), 2)

    def test_ab_pos_request_accepts_all_groups(self):
        req = self._create_request('AB+')
        for bg, _ in BloodRequest.BloodGroup.choices:
            self._create_donor(f'd_{bg}@e.com', bg)
        
        results = find_eligible_donors(req)
        self.assertEqual(len(results), 8)

    def test_ab_neg_request_accepts_ab_neg_a_neg_b_neg_o_neg(self):
        req = self._create_request('AB-')
        for bg, _ in BloodRequest.BloodGroup.choices:
            self._create_donor(f'd_{bg}@e.com', bg)
            
        results = find_eligible_donors(req)
        self.assertEqual(len(results), 4)
        donors_bg = [r['donor'].blood_group for r in results]
        self.assertCountEqual(donors_bg, ['AB-', 'A-', 'B-', 'O-'])

    # ELIGIBILITY TESTS
    def test_unavailable_donor_excluded(self):
        req = self._create_request('O+')
        self._create_donor('d1@e.com', 'O+', is_available=False)
        self.assertEqual(len(find_eligible_donors(req)), 0)

    def test_donor_with_no_last_donation_date_accepted(self):
        req = self._create_request('O+')
        self._create_donor('d1@e.com', 'O+', last_donation=None)
        self.assertEqual(len(find_eligible_donors(req)), 1)

    def test_donor_donated_less_than_90_days_ago_excluded(self):
        req = self._create_request('O+')
        self._create_donor('d1@e.com', 'O+', last_donation=self.today - datetime.timedelta(days=89))
        self.assertEqual(len(find_eligible_donors(req)), 0)

    def test_donor_donated_exactly_90_days_ago_accepted(self):
        req = self._create_request('O+')
        self._create_donor('d1@e.com', 'O+', last_donation=self.today - datetime.timedelta(days=90))
        self.assertEqual(len(find_eligible_donors(req)), 1)

    def test_donor_donated_more_than_90_days_ago_accepted(self):
        req = self._create_request('O+')
        self._create_donor('d1@e.com', 'O+', last_donation=self.today - datetime.timedelta(days=91))
        self.assertEqual(len(find_eligible_donors(req)), 1)

    # LOCATION TESTS
    def test_haversine_calculation_works(self):
        # Paris and London
        paris = (48.8566, 2.3522)
        london = (51.5074, -0.1278)
        dist = calculate_distance_km(paris[0], paris[1], london[0], london[1])
        self.assertAlmostEqual(dist, 343.5, places=0)

    def test_nearby_donor_gets_smaller_distance(self):
        req = self._create_request('O+', lat=0.0, lon=0.0)
        d_near = self._create_donor('near@e.com', 'O+', lat=0.0, lon=0.1) # approx 11km
        d_far = self._create_donor('far@e.com', 'O+', lat=0.0, lon=1.0) # approx 111km
        
        results = find_eligible_donors(req)
        # Results are sorted by score then distance, both have score 50 (since > 10 and > 50 gives 75/25, wait!)
        # Actually >10 is 75, >50 is 25. Let's just check the calculated values.
        res_near = next(r for r in results if r['donor'] == d_near)
        res_far = next(r for r in results if r['donor'] == d_far)
        self.assertLess(res_near['distance_km'], res_far['distance_km'])

    def test_missing_donor_coordinates_produce_none_distance(self):
        req = self._create_request('O+', lat=0.0, lon=0.0)
        self._create_donor('d@e.com', 'O+', lat=None, lon=None)
        results = find_eligible_donors(req)
        self.assertIsNone(results[0]['distance_km'])

    def test_missing_request_coordinates_produce_none_distance(self):
        req = self._create_request('O+', lat=None, lon=None)
        self._create_donor('d@e.com', 'O+', lat=0.0, lon=0.0)
        results = find_eligible_donors(req)
        self.assertIsNone(results[0]['distance_km'])

    # SCORING TESTS
    def _test_distance_score(self, distance, expected_score):
        # We manipulate the helper function by creating coords that yield exact distances is hard.
        # Let's mock calculate_distance_km or just create specific coordinates.
        # Actually, 1 degree lat is ~111.32 km.
        req = self._create_request('O+', lat=0.0, lon=0.0)
        lat_offset = distance / 111.139 # close enough for great circle on equator
        self._create_donor(f'd_{distance}@e.com', 'O+', lat=lat_offset, lon=0.0)
        # However, to be precise, let's just patch it or rely on exact values.
        pass

    def test_distance_scoring_buckets(self):
        req = self._create_request('O+', lat=0.0, lon=0.0)
        
        # 4km -> 100
        # 8km -> 90
        # 15km -> 75
        # 30km -> 50
        # 60km -> 25
        # We can approximate with lat offsets (1 degree = 111.139 km)
        d_4km = self._create_donor('d4@e.com', 'O+', lat=4/111.139, lon=0.0)
        d_8km = self._create_donor('d8@e.com', 'O+', lat=8/111.139, lon=0.0)
        d_15km = self._create_donor('d15@e.com', 'O+', lat=15/111.139, lon=0.0)
        d_30km = self._create_donor('d30@e.com', 'O+', lat=30/111.139, lon=0.0)
        d_60km = self._create_donor('d60@e.com', 'O+', lat=60/111.139, lon=0.0)
        
        results = find_eligible_donors(req)
        scores = {r['donor'].user.email: r['score'] for r in results}
        
        self.assertEqual(scores['d4@e.com'], 100)
        self.assertEqual(scores['d8@e.com'], 90)
        self.assertEqual(scores['d15@e.com'], 75)
        self.assertEqual(scores['d30@e.com'], 50)
        self.assertEqual(scores['d60@e.com'], 25)

    def test_missing_distance_gets_base_score_50(self):
        req = self._create_request('O+', lat=None, lon=None)
        self._create_donor('d@e.com', 'O+')
        results = find_eligible_donors(req)
        self.assertEqual(results[0]['score'], 50)

    def test_urgent_adds_5(self):
        req = self._create_request('O+', urgency=BloodRequest.Urgency.URGENT, lat=None, lon=None)
        self._create_donor('d@e.com', 'O+')
        results = find_eligible_donors(req)
        # Base 50 + 5 = 55
        self.assertEqual(results[0]['score'], 55)

    def test_critical_adds_10(self):
        req = self._create_request('O+', urgency=BloodRequest.Urgency.CRITICAL, lat=None, lon=None)
        self._create_donor('d@e.com', 'O+')
        results = find_eligible_donors(req)
        # Base 50 + 10 = 60
        self.assertEqual(results[0]['score'], 60)

    def test_score_never_exceeds_100(self):
        # 4km -> 100. Critical adds 10. Max should be 100.
        req = self._create_request('O+', urgency=BloodRequest.Urgency.CRITICAL, lat=0.0, lon=0.0)
        self._create_donor('d@e.com', 'O+', lat=4/111.139, lon=0.0)
        results = find_eligible_donors(req)
        self.assertEqual(results[0]['score'], 100)

    # MATCHING TESTS
    def test_incompatible_donor_excluded(self):
        req = self._create_request('O-')
        self._create_donor('d@e.com', 'O+')
        results = find_eligible_donors(req)
        self.assertEqual(len(results), 0)

    def test_compatible_available_eligible_donor_returned(self):
        req = self._create_request('O+')
        d = self._create_donor('d@e.com', 'O-')
        results = find_eligible_donors(req)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['donor'], d)

    def test_results_sorted_by_score_descending(self):
        req = self._create_request('O+', lat=0.0, lon=0.0)
        # d_far gets score 25
        d_far = self._create_donor('far@e.com', 'O+', lat=60/111.139, lon=0.0)
        # d_near gets score 100
        d_near = self._create_donor('near@e.com', 'O+', lat=4/111.139, lon=0.0)
        
        results = find_eligible_donors(req)
        self.assertEqual(results[0]['donor'], d_near)
        self.assertEqual(results[1]['donor'], d_far)

    def test_distance_breaks_equal_score_matches(self):
        req = self._create_request('O+', lat=0.0, lon=0.0)
        # Both in 10-20km bracket (score 75)
        d_18 = self._create_donor('d18@e.com', 'O+', lat=18/111.139, lon=0.0)
        d_12 = self._create_donor('d12@e.com', 'O+', lat=12/111.139, lon=0.0)
        
        results = find_eligible_donors(req)
        # Both score 75. Smaller distance should be first.
        self.assertEqual(results[0]['donor'], d_12)
        self.assertEqual(results[1]['donor'], d_18)

    def test_no_eligible_donors_returns_empty_result(self):
        req = self._create_request('O+')
        # No donors created
        self.assertEqual(find_eligible_donors(req), [])
