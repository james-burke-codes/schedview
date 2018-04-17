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

import models
from models import Base, Job, Employee

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

        with self.subTest(name="post successful request"):
            with boddle(method='POST', json={"name": "test1", "title": "test1"}):
                self.assertEqual(service.post_employee(db=self.db),
                    '{"id": 1, "name": "test1", "title": "test1"}')


        with self.subTest(name="index successful request"):
            with boddle(method='GET'):
                self.assertEqual(service.index(db=self.db),
                    '[{"id": 1, "name": "test1", "title": "test1"}]')


        with self.subTest(name="get successful request"):
            with boddle(method='GET'):
                self.assertEqual(service.get_employee(db=self.db, employee_id=1),
                    '{"id": 1, "name": "test1", "title": "test1"}')


        with self.subTest(name="put successful request"):
            with boddle(method='PUT', json={"name": "test2", "title": "test2"}):
                self.assertEqual(service.put_employee(db=self.db, employee_id=1),
                    '{"id": 1, "name": "test2", "title": "test2"}')


        # add Job record
        job = Job(name='test1')
        self.db.add(job)
        # add Employee record
        employee = Employee(name='test1', title='test2')
        self.db.add(employee)
        self.db.commit()

        with self.subTest(name="post successful availability request"):
            with boddle(method='POST', json={"job_id": job.id, "employee_id": employee.id, "availability": {'mon': [9,16]}}):
                self.assertEqual(service.post_employee_availability(db=self.db),
                    '{"job_id": 1, "employee_id": 2, "availability": "{\\"mon\\": [9, 16]}"}')

        with self.subTest(name="put successful availability request"):
            with boddle(method='PUT', json={"job_id": job.id, "employee_id": employee.id, "availability": {'tue': [9,10]}}):
                self.assertEqual(service.put_employee_availability(db=self.db),
                    '{"job_id": 1, "employee_id": 2, "availability": "{\\"tue\\": [9, 10]}"}')


    def test_failure(self):

        # add Employee record
        employee = Employee(name='test1', title='test2')
        self.db.add(employee)
        self.db.commit()

        with self.subTest(name="put invalid content_type"):
            with boddle(method='PUT'):
                self.assertEqual(service.put_employee(db=self.db, employee_id=1),
                    'invalid request, expected header-content_type: application/json')


        # add Job record
        job = Job(name='test1')
        self.db.add(job)

        with self.subTest(name="put invalid availability"):
            with boddle(method='PUT', json={"job_id": job.id, "employee_id": employee.id, "availability": {'ddd': [9,10]}}):
                self.assertEqual(service.post_employee_availability(db=self.db),
                    "Invalid day values, must be: 'mon', 'tue', 'wed', 'thur', 'fri'")

        with self.subTest(name="put invalid availability"):
            with boddle(method='PUT', json={"job_id": job.id, "employee_id": employee.id, "availability": {'tue': [6,10]}}):
                self.assertEqual(service.post_employee_availability(db=self.db),
                    "Invalid time range, must be between: 9 and 17")




if __name__ == '__main__':
    unittest.main()
