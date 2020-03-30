import unittest

from report import Report


class TestReportHolder(unittest.TestCase):

    def test_report_single_error(self):
        report = Report()
        message = "first error"
        report.error(message)
        self.assertEqual(report.error_messages()[0], message)
        self._count_match(report, errors=1)

    def test_report_single_warning(self):
        report = Report()
        message = "first warning"
        report.warning(message)
        self.assertEqual(report.warning_messages()[0], message)
        self._count_match(report, warnings=1)

    def test_report_single_notice(self):
        report = Report()
        message = "first notice"
        report.notice(message)
        self.assertEqual(report.notice_messages()[0], message)
        self._count_match(report, notices=1)

    def test_report_error_with_other_messages(self):
        report = Report()
        message = "first error"
        report.notice("a notice")
        report.notice("another notice")
        report.warning("a warning")
        report.error(message)
        self.assertEqual(report.error_messages()[0], message)
        self._count_match(report, errors=1, warnings=1, notices=2)

    def _count_match(self, report, errors=0, warnings=0, notices=0):
        worst = "{}:".format(_worst(errors=errors, warnings=warnings, notices=notices))
        self.assertEqual(report.errors, errors)
        self.assertEqual(report.warnings, warnings)
        self.assertEqual(report.notices, notices)
        self.assertEqual(report.errors, len(report.error_messages()))
        self.assertEqual(report.warnings, len(report.warning_messages()))
        self.assertEqual(report.notices, len(report.notice_messages()))
        self.assertTrue(str(report).startswith(worst))
        self.assertEqual(report.has_errors, errors > 0)
        self.assertEqual(report.has_warnings, errors > 0 or warnings > 0)
        self.assertEqual(len(report) + 0, errors + warnings + notices)


def _worst(errors=0, warnings=0, notices=0):
    if errors > 0:
        worst = "ERRORS"
    elif warnings > 0:
        worst = "WARNINGS"
    elif notices > 0:
        worst = "NOTICES"
    else:
        worst = "NONE"
    return worst


if __name__ == '__main__':
    unittest.main()
