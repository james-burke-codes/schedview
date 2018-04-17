#!env/bin/python3
import os
import sys
import json
import unittest
from unittest.mock import patch
from boddle import boddle

import logging
from candidate import service as candidate
from employee import service as employee
from job import service as job

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from models import Base

class FunctionalTestCase(unittest.TestCase):

    def setUp(self):
        candidate.builtins.alchemyencoder = lambda x: None
        employee.builtins.alchemyencoder = lambda x: None

        Session = sessionmaker()
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        Session.configure(bind=self.engine)
        Base.metadata.create_all(self.engine)
        self.db = Session()


    def tearDown(self):
        Base.metadata.drop_all(self.engine)

    def test_create_employee_create_candidate_compare_availability(self):

        ## create candidate
        #with self.subTest(name="post successful request"):
        with boddle(method='POST', json={"name": "test1"}):
            self.assertEqual(candidate.post_candidate(db=self.db),
                '{"id": 1, "name": "test1"}')

        with boddle(method='GET'):
            candidate_record = json.loads(candidate.index(db=self.db))[0]


        ## create employee
        #with self.subTest(name="post successful request"):
        with boddle(method='POST', json={"name": "test1", "title": "test1"}):
            self.assertEqual(employee.post_employee(db=self.db),
                '{"id": 1, "name": "test1", "title": "test1"}')

        with boddle(method='GET'):
            employee_record = json.loads(employee.index(db=self.db))[0]


        ## setup job
        #with self.subTest(name="post successful request"):
        with boddle(method='POST', json={"name": "test2"}):
            self.assertEqual(job.post_job(db=self.db),
                '{"id": 1, "name": "test2"}')

        with boddle(method='GET'):
            job_record = json.loads(job.index(db=self.db))[0]

        ## add availability for candidate
        with self.subTest(name="post successful availability request"):
            with boddle(method='POST', json={"job_id": job_record['id'], "candidate_id": candidate_record['id'], "availability": {'mon': [9,16]}}):
                self.assertEqual(candidate.post_candidate_availability(db=self.db),
                    '{"job_id": 1, "candidate_id": 1, "availability": "{\\"mon\\": [9, 16]}"}')

        ## add availability for employee
        with self.subTest(name="post successful availability request"):
            with boddle(method='POST', json={"job_id": job_record['id'], "employee_id": employee_record['id'], "availability": {'mon': [9,16]}}):
                self.assertEqual(employee.post_employee_availability(db=self.db),
                    '{"job_id": 1, "employee_id": 1, "availability": "{\\"mon\\": [9, 16]}"}')



if __name__ == '__main__':
    unittest.main()