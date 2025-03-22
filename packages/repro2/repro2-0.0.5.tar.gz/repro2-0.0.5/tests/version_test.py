import unittest

import repro2


class TestVersion(unittest.TestCase):
    def test_version_exists(self):
        assert repro2.VERSION
