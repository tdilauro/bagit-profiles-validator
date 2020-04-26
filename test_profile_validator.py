from copy import deepcopy
import json
import unittest

from profile import Profile
from report import Report
from profile_validator import ProfileValidator


class TestProfileValidator(unittest.TestCase):

    def setUp(self):
        json_string = sample_profile_v1_3_0()
        self.profile_dict = json.loads(json_string)
        self.profile = Profile.from_json(json_string)

    def _get_safe_profile_dict(self):
        return deepcopy(self.profile_dict)

    def test_ValidationOfValidProfileShouldSucceed(self):
        report = Report()
        self.validator = ProfileValidator(self.profile, report=report, fail_on_warning=False)
        success = self.validator.validate()
        self.assertTrue(success)

    def test_BagItProfileInfoSectionMustBePresent(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        del(profile_dict["BagIt-Profile-Info"])
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report)
        success = validator.validate()
        self.assertFalse(success)
        self.assertGreater(len(profile), 0)
        self.assertIn("Required 'BagIt-Profile-Info' section is missing", report.error_messages()[0])

    def test_BagInfoTagDescriptionShouldNotBeABooleanGivesWarning(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        profile_dict["Bag-Info"] = {"FakeTag": {"description": False}}
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report)
        validator.validate()
        self.assertEqual(len(report.warning_messages()), 1)
        self.assertIn("tag 'description' property, when present, must be a string.", report.warning_messages()[0])

    def test_BagInfoTagDescriptionShouldNotBeANumberGivesWarning(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        profile_dict["Bag-Info"] = {"FakeTag": {"description": 0}}
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report)
        validator.validate()
        self.assertEqual(len(report.warning_messages()), 1)
        self.assertIn("tag 'description' property, when present, must be a string.", report.warning_messages()[0])

    def test_BagInfoTagDescriptionShouldBeAString(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        profile_dict["Bag-Info"] = {"FakeTag": {"description": "some string"}}
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report)
        success = validator.validate()
        self.assertTrue(success)
        self.assertEqual(len(report.messages()), 0)

    def test_WarningShouldResultInFailureWhenFailOnWarningTrue(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        profile_dict["Bag-Info"] = {"FakeTag": {"description": False}}
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report, fail_on_warning=True)
        success = validator.validate()
        self.assertFalse(success)
        self.assertEqual(len(report.warning_messages()), 1)

    def test_WarningShouldNotCauseFailureWhenFailOnWarningFalse(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        profile_dict["Bag-Info"] = {"FakeTag": {"description": False}}
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report, fail_on_warning=False)
        success = validator.validate()
        self.assertTrue(success)
        self.assertEqual(len(report.warning_messages()), 1)

    def test_WarningShouldNotCauseFailureWhenFailOnWarningUnset(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        profile_dict["Bag-Info"] = {"FakeTag": {"description": False}}
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report)
        success = validator.validate()
        self.assertTrue(success)
        self.assertEqual(len(report.warning_messages()), 1)

    def test_PayloadManifestAllowedRequiredConsistency(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        profile_dict["Manifests-Allowed"] = ["foo"]
        profile_dict["Manifests-Required"] = ["sha256"]
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report)
        success = validator.validate()
        self.assertFalse(success)
        self.assertEqual(len(report.error_messages()), 1)
        self.assertRegexpMatches(report.error_messages()[0],
                                 r'Required payload manifest type.+not allowed by Manifests-Allowed')

    def test_TagManifestAllowedRequiredConsistency(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        profile_dict["Tag-Manifests-Allowed"] = ["foo"]
        profile_dict["Tag-Manifests-Required"] = ["sha256"]
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report)
        success = validator.validate()
        self.assertFalse(success)
        self.assertEqual(len(report.error_messages()), 1)
        self.assertRegexpMatches(report.error_messages()[0],
                                 r'Required tag manifest type.+not allowed by Tag-Manifests-Allowed')

    def test_AllowMorePayloadManifestsThanRequired(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        profile_dict["Manifests-Allowed"] = ["sha256", "sha512"]
        profile_dict["Manifests-Required"] = ["sha256"]
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report)
        success = validator.validate()
        self.assertTrue(success)
        self.assertEqual(len(report.messages()), 0)

    def test_AllowMoreTagManifestsThanRequired(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        profile_dict["Tag-Manifests-Allowed"] = ["sha256", "sha512"]
        profile_dict["Tag-Manifests-Required"] = ["sha256"]
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report)
        success = validator.validate()
        self.assertTrue(success)
        self.assertEqual(len(report.messages()), 0)

    def test_RequiredTagFilesNotAllowed(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        profile_dict["Tag-Files-Allowed"] = []
        profile_dict["Tag-Files-Required"] = ["tag-foo"]
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report)
        success = validator.validate()
        self.assertFalse(success)
        self.assertEqual(len(report.messages()), 1)
        self.assertRegexpMatches(report.error_messages()[0],
                                 r'Required tag files .+ not listed in Tag-Files-Allowed')

    def test_RequiredTagFilesOkayIfAllowedNotSpecified(self):
        report = Report()
        profile_dict = self._get_safe_profile_dict()
        # delete "Tag-Files-Allowed" property, if present
        _ = profile_dict.pop("Tag-Files-Allowed", None)
        profile_dict["Tag-Files-Required"] = ["tag-foo"]
        profile = Profile.from_dict(profile_dict)
        validator = ProfileValidator(profile, report=report)
        success = validator.validate()
        self.assertTrue(success)
        self.assertEqual(len(report.messages()), 0)


def sample_profile_v1_3_0():
    return """
        {
           "BagIt-Profile-Info": {
              "BagIt-Profile-Identifier": "TEST",
              "BagIt-Profile-Version": "1.3.0",
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
