import main
import unittest
import os
import shutil

class TestQRCodeSaving(unittest.TestCase):
    def setUp(self):
        # Clean up qrcodes directory before test
        if os.path.exists('qrcodes'):
            shutil.rmtree('qrcodes')
        os.makedirs('qrcodes')

    def test_save_generated_images(self):
        print("Testing file saving...")
        with main.app.test_client() as client:
            response = client.get('/qrcodes')
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"Saved", response.data)
            
            # Check if files exist
            for i in range(1, 11):
                filename = f'qrcodes/slot{i}.png'
                self.assertTrue(os.path.exists(filename), f"{filename} does not exist")
                self.assertTrue(os.path.getsize(filename) > 0, f"{filename} is empty")
                
        print("File Saving Test Passed")

if __name__ == '__main__':
    unittest.main()
