import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from junit_delta import compare, load


class JUnitDeltaTests(unittest.TestCase):
    def parse(self, text):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'report.xml'
            p.write_bytes(text.encode('utf-8'))
            return load(p)

    def test_nested_suite_identity_and_logs_excluded(self):
        cases = self.parse('<testsuites><testsuite name="a"><testsuite name="b"><testcase classname="c" name="x" time="0.2"><system-out>secret</system-out></testcase></testsuite></testsuite></testsuites>')
        self.assertEqual(list(cases), [('a', 'b', 'c', 'x')])
        self.assertNotIn('secret', json.dumps(cases[('a', 'b', 'c', 'x')]))

    def test_failure_recovery_and_new_failure(self):
        a = self.parse('<testsuite name="s"><testcase name="a"><failure/></testcase><testcase name="b"/></testsuite>')
        b = self.parse('<testsuite name="s"><testcase name="a"/><testcase name="b"><error/></testcase></testsuite>')
        out = compare(a, b)
        self.assertEqual(out['regressions'], 1)
        self.assertEqual(out['changes'][0]['after']['state'], 'passed')

    def test_duration_thresholds_and_unknown_not_zero(self):
        a = self.parse('<testsuite name="s"><testcase name="x" time="1"/><testcase name="y"/></testsuite>')
        b = self.parse('<testsuite name="s"><testcase name="x" time="1.6"/><testcase name="y" time="100"/></testsuite>')
        self.assertEqual(compare(a, b)['regressions'], 1)
        self.assertEqual(compare(a, b, minimum=1)['regressions'], 0)

    def test_new_skip_and_removal(self):
        a = self.parse('<testsuite name="s"><testcase name="x"/></testsuite>')
        b = self.parse('<testsuite name="s"><testcase name="y"><skipped/></testcase></testsuite>')
        self.assertEqual(compare(a, b)['removed'], 1)
        self.assertEqual(compare(a, b)['regressions'], 1)

    def test_duplicate_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            self.parse('<testsuite name="s"><testcase name="x"/><testcase name="x"/></testsuite>')

    def test_dtd_and_nonfinite_rejected(self):
        for xml in ['<!DOCTYPE x [<!ENTITY y "expanded">]><testsuite name="s"/>', '<testsuite name="s"><testcase name="x" time="NaN"/></testsuite>', '<testsuite name="s"><testcase name="x" time="-1"/></testsuite>']:
            with self.assertRaises(ValueError):
                self.parse(xml)

    def test_ambiguous_outcome_and_namespace_rejected(self):
        for xml in ['<testsuite name="s"><testcase name="x"><failure/><skipped/></testcase></testsuite>', '<testsuite xmlns="other" name="s"/>']:
            with self.assertRaises(ValueError):
                self.parse(xml)

    def test_cli_gates_and_utf16_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a.xml', Path(directory)/'b.xml'
            a.write_text('<testsuite name="s"><testcase name="x"/></testsuite>')
            b.write_text('<testsuite name="s"/>')
            command = [sys.executable, '-m', 'junit_delta', str(a), str(b)]
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 1)
            self.assertEqual(subprocess.run(command+['--allow-removed'], capture_output=True).returncode, 0)
            b.write_bytes('<?xml version="1.0" encoding="UTF-16"?><testsuite name="s"/>'.encode('utf-16'))
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)


if __name__ == '__main__':
    unittest.main()
