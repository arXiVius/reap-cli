import unittest
import os
import shutil
from reap.engine import detect_engine
from reap.utils import print_msg

class TestReapCore(unittest.TestCase):

    def test_engine_detection(self):
        """Verify that at least one scraping engine is installed on the host system."""
        engine = detect_engine()
        self.assertIn(engine, [None, "wget", "wget2"], "Engine detection returned unexpected value")
        
        if engine is None:
            print("\n[!] Warning: Neither wget nor wget2 detected. Installing one is recommended for reap.")
        else:
            print(f"\n[+] Detected local scraping engine: {engine}")

    def test_temp_directory_creation(self):
        """Verify file utility helpers create directories as expected."""
        test_dir = "reap_test_temp"
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            
        os.makedirs(test_dir, exist_ok=True)
        self.assertTrue(os.path.isdir(test_dir), "Failed to generate test directory")
        
        # Cleanup
        shutil.rmtree(test_dir)

if __name__ == "__main__":
    unittest.main()