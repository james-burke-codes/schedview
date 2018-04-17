#!env/bin/python3
import os
import sys
import unittest
from unittest.mock import patch
from boddle import boddle
import logging

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../')

import candidate_service as service

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from models import Base, Job, Candidate

class CandidateTestCase(unittest.TestCase):

    def setUp(self):
        service.builtins.alchemyencoder = lambda x: None

        Session = sessionmaker()
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Session.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.db = Session()


    def tearDown(self):
        Base.metadata.drop_all(self.engine)


    def test_success(self):

        with self.subTest(name="index successful request empty"):
            with boddle(method='GET'):
                self.assertEqual(service.index(db=self.db), '[]')

        with self.subTest(name="post successful request"):
            with boddle(method='POST', json={"name": "test1"}):
                self.assertEqual(service.post_candidate(db=self.db),
                    '{"id": 1, "name": "test1"}')


        with self.subTest(name="index successful request"):
            with boddle(method='GET'):
                self.assertEqual(service.index(db=self.db),
                    '[{"id": 1, "name": "test1"}]')


        with self.subTest(name="get successful request"):
            with boddle(method='GET'):
                self.assertEqual(service.get_candidate(db=self.db, candidate_id=1),
                    '{"id": 1, "name": "test1"}')


        with self.subTest(name="put successful request"):
            with boddle(method='PUT', json={"name": "test2"}):
                self.assertEqual(service.put_candidate(db=self.db, candidate_id=1),
                    '{"id": 1, "name": "test2"}')

        # add Job record
        job = Job(name='test1')
        self.db.add(job)
        # add Candidate record
        candidate = Candidate(name='test1')
        self.db.add(candidate)
        self.db.commit()

        with self.subTest(name="post successful availability request"):
            with boddle(method='POST', json={"job_id": job.id, "candidate_id": candidate.id, "availability": {'mon': [9,16]}}):
                self.assertEqual(service.post_candidate_availability(db=self.db),
                    '{"job_id": 1, "candidate_id": 2, "availability": "{\\"mon\\": [9, 16]}"}')

        with self.subTest(name="put successful availability request"):
            with boddle(method='PUT', json={"job_id": job.id, "candidate_id": candidate.id, "availability": {'tue': [9,10]}}):
                self.assertEqual(service.put_candidate_availability(db=self.db),
                    '{"job_id": 1, "candidate_id": 2, "availability": "{\\"tue\\": [9, 10]}"}')


    def test_failure(self):

        # add records
        candidate = Candidate(name='test1')
        self.db.add(candidate)
        self.db.commit()

        with self.subTest(name="put invalid content_type for put_candidate"):
            with boddle(method='PUT'):
                self.assertEqual(service.put_candidate(db=self.db, candidate_id=1),
                    'invalid request, expected header-content_type: application/json')


        with self.subTest(name="post invalid content_type for post_candidate"):
            with boddle(method='POST'):
                self.assertEqual(service.post_candidate(db=self.db),
                    'invalid request, expected header-content_type: application/json')


        with self.subTest(name="post invalid content_type for post_candidate_availability"):
            with boddle(method='POST'):
                self.assertEqual(service.post_candidate_availability(db=self.db),
                    'invalid request, expected header-content_type: application/json')


        with self.subTest(name="put invalid content_type for put_candidate_availability"):
            with boddle(method='PUT'):
                self.assertEqual(service.put_candidate_availability(db=self.db),
                    'invalid request, expected header-content_type: application/json')


        with self.subTest(name="put invalid request with wrong payload data"):
            with boddle(method='PUT', json={"name1": "test2"}):
                self.assertEqual(service.put_candidate(db=self.db, candidate_id=1),
                    "invalid request, no value for 'name' given")


        # add Job record
        job = Job(name='test1')
        self.db.add(job)

        with self.subTest(name="put invalid availability wrong day of the week"):
            with boddle(method='PUT', json={"job_id": job.id, "candidate_id": candidate.id, "availability": {'ddd': [9,10]}}):
                self.assertEqual(service.post_candidate_availability(db=self.db),
                    "Invalid day values, must be: 'mon', 'tue', 'wed', 'thur', 'fri'")

        with self.subTest(name="put invalid availability wrong hours"):
            with boddle(method='PUT', json={"job_id": job.id, "candidate_id": candidate.id, "availability": {'tue': [6,10]}}):
                self.assertEqual(service.post_candidate_availability(db=self.db),
                    "Invalid time range, must be between: 9 and 17")




if __name__ == '__main__':
    unittest.main()