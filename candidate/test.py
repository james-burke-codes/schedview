import os
import sys
import unittest
from unittest.mock import patch
from boddle import boddle

import logging
import service

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

from models import Base, Candidate

class CandidateTestCase(unittest.TestCase):

    def setUp(self):
        service.builtins.alchemyencoder = lambda x: None

        Session = sessionmaker()
        self.engine = create_engine("sqlite:///:memory:", echo=True)
        Session.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.db = Session()


    def tearDown(self):
        Base.metadata.drop_all(self.engine)


    def test_success(self):

        with self.subTest(name="index successful request empty"):
            with boddle(method='GET'):
               self.assertEqual(service.index(db=self.db), '[]')

        # add records
        self.db.add(Candidate(name='test1'))
        self.db.commit()

        with self.subTest(name="index successful request"):
            with boddle(method='GET'):
               self.assertEqual(service.index(db=self.db), '[{"id": 1, "name": "test1"}]')


        with self.subTest(name="get successful request"):
            with boddle(method='GET'):
               self.assertEqual(service.get_candidate(db=self.db, candidate_id=1), '{"id": 1, "name": "test1"}')


        with self.subTest(name="put successful request"):
            with boddle(method='PUT', json={"name": "test2"}):
               self.assertEqual(service.put_candidate(db=self.db, candidate_id=1), '{"id": 1, "name": "test2"}')


        with self.subTest(name="post successful request"):
            with boddle(method='POST', json={"name": "test2"}):
               self.assertEqual(service.post_candidate(db=self.db), '{"id": 2, "name": "test2"}')

    def test_failure(self):

        # add records
        self.db.add(Candidate(name='test1'))
        self.db.commit()

        with self.subTest(name="put invalid content_type"):
            with boddle(method='PUT'):
               self.assertEqual(service.put_candidate(db=self.db, candidate_id=1), 'invalid request, expected header-content_type: application/json')


if __name__ == '__main__':
    unittest.main()