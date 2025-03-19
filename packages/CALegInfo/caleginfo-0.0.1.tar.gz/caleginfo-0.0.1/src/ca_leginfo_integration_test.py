"""Unit tests for ca_leginfo.py."""

import ca_leginfo

import unittest
import logging

logging.basicConfig(level=logging.DEBUG)

class CALegInfoClientTests(unittest.TestCase):
    """Integration tests for CALegInfoClient.
    
    These are "live" integration tests.  
    
    By design they use the live API and will fail if the upstream website
      gets changed.
    """

    def setUp(self):
        self._client = ca_leginfo.CALegInfoClient()

    def test_get_bill_title(self):
        """Tests that get bill author can correctly return an author."""
        got = self._client.get_bill_title(bill_id='202320240AB1939')
        want = "AB-1939 Pupil attendance"
        self.assertIn(want, got)
    
    def test_bill_status(self):
        """Tests that bill status returns properly."""
        got = self._client.get_bill_status(bill_id='202320240AB1939')
        self.assertEqual(got.lead_author, 'Maienschein (A)')
        self.assertEqual(got.topic,
                         'Pupil attendance: county and local school attendance review boards: pupil consultation.')
        self.assertEqual(got.house_location, 'Secretary of State')
        self.assertEqual(got.last_amended, '06/14/24')
        self.assertEqual(got.committee_location, None)
        self.assertEqual(got.history[0], 
                         {'date': '06/14/24', 
                          'action': 'Chaptered by Secretary of State - Chapter 13, Statutes of 2024.'})
        
    def test_bill_list_full_list(self):
        """Tests that we can list all bills for a session."""
        got = self._client.get_bill_list(session_id='20232024')
        self.assertEqual(len(got), 5564)
    
    def test_bill_list_filtered_budget(self):
        got = self._client.get_bill_list(session_id='20232024', filter="Budget Act")
        self.assertEqual(len(got), 5443)
    
    def test_bill_digest_succeeds(self):
        got = self._client.get_bill_digest(bill_id='202320240AB1939')
        self.assertIn('Existing law authorizes the establishment of county school attendance review', got)
                                         

if __name__ == '__main__':
    unittest.main()