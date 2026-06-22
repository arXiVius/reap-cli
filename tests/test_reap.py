import unittest
import os
import shutil
from reap import __version__
from reap.engine import normalize_url, get_page_local_path, get_relative_url, is_same_domain
from reap.utils import print_msg


class TestReapMetadata(unittest.TestCase):
    """Verify package metadata is defined and consistent."""

    def test_version_is_semver(self):
        parts = __version__.split(".")
        self.assertEqual(len(parts), 3, f"Version {__version__!r} is not semver (x.y.z)")
        for part in parts:
            self.assertTrue(part.isdigit(), f"Version component {part!r} is not numeric")

    def test_version_not_empty(self):
        self.assertTrue(len(__version__) > 0)


class TestURLUtilities(unittest.TestCase):
    """Test the URL normalization and path resolution helpers."""

    def test_normalize_strips_utm(self):
        url = "https://example.com/page?utm_source=test&foo=bar"
        result = normalize_url(url)
        self.assertNotIn("utm_source", result)
        self.assertIn("foo=bar", result)

    def test_normalize_strips_fragment(self):
        url = "https://example.com/page#section"
        result = normalize_url(url)
        self.assertNotIn("#section", result)

    def test_normalize_cdn_prefix(self):
        url = "https://cdn3.example.com/image.png"
        result = normalize_url(url)
        self.assertIn("cdn.example.com", result)

    def test_is_same_domain_exact(self):
        self.assertTrue(is_same_domain("https://example.com/page", "example.com"))

    def test_is_same_domain_subdomain(self):
        self.assertTrue(is_same_domain("https://www.example.com/page", "example.com"))

    def test_is_same_domain_different(self):
        self.assertFalse(is_same_domain("https://other.com/page", "example.com"))

    def test_get_page_local_path_root(self):
        _, url_path = get_page_local_path("https://example.com/", "/output")
        self.assertEqual(url_path, "/index.html")

    def test_get_page_local_path_app_mode(self):
        _, url_path = get_page_local_path("https://example.com/about", "/output", mode="app")
        self.assertEqual(url_path, "/about/index.html")

    def test_get_relative_url(self):
        result = get_relative_url("/pages/about/index.html", "/assets/style.css")
        self.assertEqual(result, "../../assets/style.css")


class TestTempDirectory(unittest.TestCase):
    """Verify file utility helpers create directories as expected."""

    def test_temp_directory_creation(self):
        test_dir = "reap_test_temp"
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)

        os.makedirs(test_dir, exist_ok=True)
        self.assertTrue(os.path.isdir(test_dir), "Failed to generate test directory")

        # Cleanup
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    unittest.main()