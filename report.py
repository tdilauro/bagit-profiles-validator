class Report(object):  # pylint: disable=useless-object-inheritance
    @staticmethod
    def _error_filter(e): return e.is_error

    @staticmethod
    def _warning_filter(e): return e.is_warning

    @staticmethod
    def _notice_filter(e): return not e.is_error and not e.is_warning

    def __init__(self):
        self._entries = []
        self._errors = 0
        self._warnings = 0
        self._notices = 0

    def error(self, message):
        self._errors += 1
        self._entries.append(_Entry.from_error(message))

    def warning(self, message):
        self._warnings += 1
        self._entries.append(_Entry.from_warning(message))

    def notice(self, message):
        self._notices += 1
        self._entries.append(_Entry.from_notice(message))

    @property
    def has_errors(self):
        return self._errors > 0

    @property
    def has_warnings(self):
        return self._errors > 0 or self._warnings > 0

    def error_messages(self):
        return self.messages(entry_filter=self._error_filter)

    def warning_messages(self):
        return self.messages(entry_filter=self._warning_filter)

    def notice_messages(self):
        return self.messages(entry_filter=self._notice_filter)

    def messages(self, entry_filter=lambda e: True):
        return [entry.message for entry in self._entries if entry_filter(entry)]

    @property
    def errors(self):
        return self._errors

    @property
    def warnings(self):
        return self._warnings

    @property
    def notices(self):
        return self._notices

    def __len__(self):
        return self._errors + self._warnings + self._notices

    def __str__(self):
        errors, warnings, notices = self._errors, self._warnings, self._notices
        if errors > 0:
            worst = "ERRORS"
        elif warnings > 0:
            worst = "WARNINGS"
        elif notices > 0:
            worst = "NOTICES"
        else:
            worst = "NONE"
        return "{}: errors={}, warnings={}, notices={}".format(worst, errors, warnings, notices)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.__str__())


class _Entry(object):
    _error_code = "E"
    _warning_code = "W"
    _notice_code = "I"

    def __init__(self, entry_type, message):
        self._type = entry_type
        self._msg = message

    @property
    def message(self):
        return self._msg

    @property
    def is_error(self):
        return self._type == self._error_code

    @property
    def is_warning(self):
        return self._type == self._warning_code

    @property
    def is_info(self):
        return self._type == self._notice_code

    # factory methods

    @classmethod
    def from_error(cls, message):
        return cls(cls._error_code, message)

    @classmethod
    def from_warning(cls, message):
        return cls(cls._warning_code, message)

    @classmethod
    def from_notice(cls, message):
        return cls(cls._notice_code, message)
