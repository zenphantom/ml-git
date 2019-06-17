"""
© Copyright 2020 HP Development Company, L.P.
SPDX-License-Identifier: GPL-2.0-only
"""

import unittest
import test.all_tests

testSuite = test.all_tests.create_test_suite()
text_runner = unittest.TextTestRunner().run(testSuite)