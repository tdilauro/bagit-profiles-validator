import json
import unittest

from profile import Profile

TEST_PROFILE_FILE = "./fixtures/bagProfileBar.json"
TEST_PROFILE_URL = "https://raw.github.com/bagit-profiles/bagit-profiles/master/bagProfileBar.json"

TOP_LEVEL_PROPERTIES = ["BagIt-Profile-Info", "Bag-Info", "Accept-BagIt-Version",
                        "Manifests-Required", "Manifests-Allowed",
                        "Allow-Fetch.txt", "Serialization", "Accept-Serialization",
                        "Tag-Manifests-Required", "Tag-Manifests-Allowed",
                        "Tag-Files-Required", "Tag-Files-Allowed"]


class BagitProfileTest(unittest.TestCase):

    def setUp(self):
        json_string_no_version = sample_profile()
        self.profile_from_string = Profile.from_json(json_string_no_version, source="no_version")
        self.profile_obj_from_string = json.loads(json_string_no_version)
        self.profile_from_file = Profile.from_file(TEST_PROFILE_FILE)
        self.profile_from_url = Profile.from_url(TEST_PROFILE_URL)

    def test_profile_source(self):
        self.assertEqual(self.profile_from_string.source, "no_version")
        self.assertEqual(self.profile_from_file.source, TEST_PROFILE_FILE)
        self.assertEqual(self.profile_from_url.source, TEST_PROFILE_URL)

    def test_profile_version(self):
        self.assertEqual(self.profile_from_string.profile_version_info, (1, 1, 0))
        self.assertEqual(self.profile_from_file.profile_version_info, (1, 2, 0))

    def test_json_serialization(self):
        profile_json = self.profile_from_string.as_json()
        profile_obj = json.loads(profile_json)
        self._serialization_test_helper(profile_obj)

    def test_initialization_from_dict(self):
        profile = Profile.from_dict(self.profile_obj_from_string)
        profile_obj = profile.as_dict()
        self._serialization_test_helper(profile_obj)

    def test_dict_serialization(self):
        profile_obj = self.profile_from_string.as_dict()
        self._serialization_test_helper(profile_obj)

    def _serialization_test_helper(self, profile_obj):
        bag_info = profile_obj["BagIt-Profile-Info"]
        valid_entries = [k for k in profile_obj if k in TOP_LEVEL_PROPERTIES]
        self.assertDictEqual(profile_obj, self.profile_obj_from_string)
        self.assertIn("BagIt-Profile-Info", profile_obj)
        self.assertIn("BagIt-Profile-Identifier", bag_info)
        self.assertEqual(len(profile_obj), len(valid_entries))


def sample_profile():
    return """
        {
           "BagIt-Profile-Info": {
              "BagIt-Profile-Identifier": "TEST",
              "Source-Organization": "bagit-profiles.py",
              "Contact-Name": "John Doe",
              "Contact-Email": "johndoe@example.org",
              "External-Description": "Test Profile",
              "Version": "1.0"
           },
           "Bag-Info": {},
           "Manifests-Required": ["sha256", "sha512"],
           "Tag-Manifests-Required": ["sha256", "sha512"],
           "Tag-Files-Required": [],
           "Allow-Fetch.txt": true,
           "Accept-BagIt-Version": ["0.97"]
        }
        """


if __name__ == '__main__':
    unittest.main()
