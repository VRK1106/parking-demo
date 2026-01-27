import main
import unittest
import json

class TestScanLogic(unittest.TestCase):
    def test_scan_flow(self):
        print("Testing Scan Logic...")
        with main.app.test_client() as client:
            # 1. Check initial state of slot 1
            response = client.get('/api/slot1')
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data.get('slot1'), 'available', "Slot 1 should be initially available")
            print("Initial state check passed (Available)")

            # 2. Simulate scanning slot 1
            print("Simulating scan of Slot 1...")
            response = client.get('/scan/slot1')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"marked as Unavailable", response.data)
            
            # 3. Check state of slot 1 (should be unavailable)
            response = client.get('/api/slot1')
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data.get('slot1'), 'unavailable', "Slot 1 should be unavailable after scan")
            print("Post-scan state check passed (Unavailable)")

            # 4. Check state of slot 2 (should still be available)
            response = client.get('/api/slot2')
            data = json.loads(response.data.decode('utf-8'))
            self.assertEqual(data.get('slot2'), 'available', "Slot 2 should remain available")
            print("Isolation check passed (Slot 2 still Available)")

        print("Scan Logic Test Passed")

if __name__ == '__main__':
    unittest.main()
