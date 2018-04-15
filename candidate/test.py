import os
import sys
import unittest
from boddle import boddle

import logging
import service

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from models import MockSqlAlchemy

class CandidateTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_list(self):

        #with self.subTest(name="invalid validate - wrong content type"):
        with boddle():
            self.assertEqual(service.index(db=None), 'Invalid input, expected application/json')

if __name__ == '__main__':
    unittest.main()