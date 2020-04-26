from collections import namedtuple
from fnmatch import fnmatch
import logging
import sys
if sys.version_info > (3,):
    basestring = str
else:
    basestring = basestring

_Test = namedtuple('_Test', ['condition', 'severity', 'message'])
_ERROR = "E"
_WARNING = "W"


class ProfileValidator(object):

    def __init__(self, profile, report=None, enable_logging=False, fail_on_warning=False):
        self.profile = profile
        self.report = report
        self.logging_enabled = enable_logging
        self.fail_on_warning = fail_on_warning

    def _error(self, msg):
        if self.report is not None:
            self.report.error(msg)
        if self.logging_enabled:
            logging.error(msg)
        return False

    def _warning(self, msg):
        if self.report is not None:
            self.report.warning(msg)
        if self.logging_enabled:
            logging.warning(msg)
        return False if self.fail_on_warning else True

    def validate(self):
        valid = True
        valid &= self._validate_bagit_profile_info()
        valid &= self._validate_accept_bagit_versions()
        valid &= self._validate_bag_info()
        valid &= self._validate_manifests_allowed()
        valid &= self._validate_tag_files_allowed()
        return valid

    # Check self.profile['bag-profile-info'] to see if "Source-Organization",
    # "External-Description", "Version" and "BagIt-Profile-Identifier" are present.
    def _validate_bagit_profile_info(self):
        valid = True
        if "BagIt-Profile-Info" not in self.profile:
            valid &= self._error("%s: Required 'BagIt-Profile-Info' section is missing." % self.profile)
        else:
            valid &= self._validate_bagit_profile_info_children()
        return valid

    def _validate_bagit_profile_info_children(self):
        valid = True
        if "Source-Organization" not in self.profile["BagIt-Profile-Info"]:
            valid &= self._error(
                "%s: Required 'Source-Organization' property is not in 'BagIt-Profile-Info'."
                % self.profile
            )
        if "Version" not in self.profile["BagIt-Profile-Info"]:
            valid &= self._warning(
                "%s: Required 'Version' property is not in 'BagIt-Profile-Info'." % self.profile
            )
        if "BagIt-Profile-Identifier" not in self.profile["BagIt-Profile-Info"]:
            valid &= self._error(
                "%s: Required 'BagIt-Profile-Identifier' property is not in 'BagIt-Profile-Info'."
                % self.profile
            )

        return valid

    def _validate_accept_bagit_versions(self):
        """
        Ensure all versions in 'Accept-BagIt-Version' are strings
        """
        valid = True
        if "Accept-BagIt-Version" in self.profile:
            for version_number in self.profile["Accept-BagIt-Version"]:
                if not isinstance(version_number, basestring):
                    valid &= self._error(
                        'Version number "%s" in "Accept-BagIt-Version" is not a string!' % version_number
                    )
        return valid

    def _validate_bag_info(self):
        valid = True
        profile = self.profile
        if 'Bag-Info' in profile:
            for tag in profile['Bag-Info']:
                config = profile['Bag-Info'][tag]
                if profile.profile_version_info >= (1, 3, 0) and \
                        'description' in config and not isinstance(config['description'], basestring):
                    valid &= self._warning(
                        "%s: Profile Bag-Info '%s' tag 'description' property, when present, must be a string." %
                        (profile, tag)
                    )
        return valid

    def _validate_manifests_allowed(self):
        valid = True
        valid &= self._validate_allowed_manifest_type(manifest_type="tag",
                                                      allowed_attribute="Tag-Manifests-Allowed",
                                                      required_attribute="Tag-Manifests-Required")
        valid &= self._validate_allowed_manifest_type(manifest_type="payload",
                                                      allowed_attribute="Manifests-Allowed",
                                                      required_attribute="Manifests-Required")
        return valid

    def _validate_allowed_manifest_type(self, manifest_type=None, allowed_attribute=None, required_attribute=None):
        valid = True
        if allowed_attribute not in self.profile:
            return valid

        allowed = self.profile[allowed_attribute]
        required = self.profile[required_attribute] if required_attribute in self.profile else []

        required_but_not_allowed = [alg for alg in required if alg not in allowed]
        if required_but_not_allowed:
            valid &= self._error(
                "%r: Required %s manifest type(s) %s not allowed by %s" %
                (self.profile, manifest_type, [str(a) for a in required_but_not_allowed], allowed_attribute)
            )
        return valid

    def _validate_tag_files_allowed(self):
        """
        Validate the ``Tag-Files-Allowed`` tag.
        """
        allowed = (
            self.profile["Tag-Files-Allowed"]
            if "Tag-Files-Allowed" in self.profile
            else ["*"]
        )
        required = (
            self.profile["Tag-Files-Required"]
            if "Tag-Files-Required" in self.profile
            else []
        )

        valid = True
        # For each member of 'Tag-Files-Required' ensure it is also in 'Tag-Files-Allowed'.
        required_but_not_allowed = [f for f in required if not fnmatch_any(f, allowed)]
        if required_but_not_allowed:
            valid &= self._error(
                "%r: Required tag files '%s' not listed in Tag-Files-Allowed"
                % (self.profile, required_but_not_allowed)
            )

        return valid


# Return true if any of the pattern fnmatches a file path
def fnmatch_any(f, pats):
    for pat in pats:
        if fnmatch(f, pat):
            return True
    return False
