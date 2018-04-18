#!env/bin/python3
import os
import sys
import json
import unittest
from unittest.mock import patch
from boddle import boddle
import logging

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from candidate import candidate_service as candidate
from employee import employee_service as employee
from job import job_service as job

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

        # create candidate
        with boddle(method='POST', json={"name": "test1"}):
            self.assertEqual(candidate.post_candidate(db=self.db),
                '{"id": 1, "name": "test1"}')
        # get that candidate
        with boddle(method='GET'):
            candidate_record = json.loads(candidate.index(db=self.db))[0]


        ## create employee
        with boddle(method='POST', json={"name": "test1", "title": "test1"}):
            self.assertEqual(employee.post_employee(db=self.db),
                '{"id": 1, "name": "test1", "title": "test1"}')
        # get that employee
        with boddle(method='GET'):
            employee_record = json.loads(employee.index(db=self.db))[0]


        ## setup job
        with boddle(method='POST', json={"name": "test2"}):
            self.assertEqual(job.post_job(db=self.db),
                '{"id": 1, "name": "test2"}')
        # get that job
        with boddle(method='GET'):
            job_record = json.loads(job.index(db=self.db))[0]

        ## add availability for candidate
        with boddle(method='POST', json={"job_id": job_record['id'],
                                         "candidate_id": candidate_record['id'],
                                         "availability": {'mon': [9,16], 'tue': [9, 16], 'wed': [10]}}):
            self.assertEqual(candidate.post_candidate_availability(db=self.db),
                '{"job_id": 1, "candidate_id": 1, "availability": "{\\"mon\\": [9, 16], \\"tue\\": [9, 16], \\"wed\\": [10]}"}')

        ## add availability for employee
        with boddle(method='POST', json={"job_id": job_record['id'],
                                         "employee_id": employee_record['id'],
                                         "availability": {'mon': [9,16], 'tue': [9]}}):
            self.assertEqual(employee.post_employee_availability(db=self.db),
                '{"job_id": 1, "employee_id": 1, "availability": "{\\"mon\\": [9, 16], \\"tue\\": [9]}"}')


        ## add get match of employee and candidate avialability times
        with self.subTest(name="get availability of interview participants"):
            with boddle(method='GET'):
                result = job.get_attendee_availability(db=self.db, job_id=job_record['id'], candidate_id=candidate_record['id'])
                self.assertEqual(json.loads(result), {"tue": [9], "mon": [16, 9]})


    def test_create_multiple_employees_create_candidate_compare_availability(self):

        # create candidate
        with boddle(method='POST', json={"name": "test1"}):
            self.assertEqual(candidate.post_candidate(db=self.db),
                '{"id": 1, "name": "test1"}')
        # get that candidate
        with boddle(method='GET'):
            candidate_record = json.loads(candidate.index(db=self.db))[0]


        ## create employee1
        with boddle(method='POST', json={"name": "test1", "title": "test1"}):
            employee_record1 = json.loads(employee.post_employee(db=self.db))
            print(employee_record1)

        ## create employee2
        with boddle(method='POST', json={"name": "test2", "title": "test2"}):
            employee_record2 = json.loads(employee.post_employee(db=self.db))


        ## setup job
        with boddle(method='POST', json={"name": "test2"}):
            self.assertEqual(job.post_job(db=self.db),
                '{"id": 1, "name": "test2"}')
        # get that job
        with boddle(method='GET'):
            job_record = json.loads(job.index(db=self.db))[0]

        ## add availability for candidate
        with boddle(method='POST', json={"job_id": job_record['id'],
                                         "candidate_id": candidate_record['id'],
                                         "availability": {'mon': [9,16], 'tue': [9,16], 'wed': [10]}}):
            self.assertEqual(candidate.post_candidate_availability(db=self.db),
                '{"job_id": 1, "candidate_id": 1, "availability": "{\\"mon\\": [9, 16], \\"tue\\": [9, 16], \\"wed\\": [10]}"}')

        ## add availability for employee1
        with boddle(method='POST', json={"job_id": job_record['id'],
                                         "employee_id": employee_record1['id'],
                                         "availability": {'mon': [9,16], 'tue': [9]}}):
            self.assertEqual(employee.post_employee_availability(db=self.db),
                '{"job_id": 1, "employee_id": 1, "availability": "{\\"mon\\": [9, 16], \\"tue\\": [9]}"}')

         ## add availability for employee2
        with boddle(method='POST', json={"job_id": job_record['id'],
                                         "employee_id": employee_record2['id'],
                                         "availability": {'mon': [9,15], 'tue': [9]}}):
            self.assertEqual(employee.post_employee_availability(db=self.db),
                '{"job_id": 1, "employee_id": 2, "availability": "{\\"mon\\": [9, 15], \\"tue\\": [9]}"}')


        ## add get match of employee and candidate avialability times
        with self.subTest(name="get availability of interview participants"):
            with boddle(method='GET'):
                result = job.get_attendee_availability(db=self.db, job_id=job_record['id'], candidate_id=candidate_record['id'])
                self.assertEqual(json.loads(result), {"tue": [9], "mon": [9]})


    def test_create_multiple_employees_create_candidate_compare_availability_failure(self):

        # create candidate
        with boddle(method='POST', json={"name": "test1"}):
            self.assertEqual(candidate.post_candidate(db=self.db),
                '{"id": 1, "name": "test1"}')
        # get that candidate
        with boddle(method='GET'):
            candidate_record = json.loads(candidate.index(db=self.db))[0]


        ## create employee1
        with boddle(method='POST', json={"name": "test1", "title": "test1"}):
            employee_record1 = json.loads(employee.post_employee(db=self.db))

        ## create employee2
        with boddle(method='POST', json={"name": "test2", "title": "test2"}):
            employee_record2 = json.loads(employee.post_employee(db=self.db))


        ## setup job
        with boddle(method='POST', json={"name": "test2"}):
            self.assertEqual(job.post_job(db=self.db),
                '{"id": 1, "name": "test2"}')
        # get that job
        with boddle(method='GET'):
            job_record = json.loads(job.index(db=self.db))[0]

        ## add availability for candidate
        with boddle(method='POST', json={"job_id": job_record['id'],
                                         "candidate_id": candidate_record['id'],
                                         "availability": {'mon': [9,16], 'tue': [9,16], 'wed': [10]}}):
            self.assertEqual(candidate.post_candidate_availability(db=self.db),
                '{"job_id": 1, "candidate_id": 1, "availability": "{\\"mon\\": [9, 16], \\"tue\\": [9, 16], \\"wed\\": [10]}"}')

        ## add availability for employee1
        with boddle(method='POST', json={"job_id": job_record['id'],
                                         "employee_id": employee_record1['id'],
                                         "availability": {'mon': [9,16], 'tue': [9]}}):
            self.assertEqual(employee.post_employee_availability(db=self.db),
                '{"job_id": 1, "employee_id": 1, "availability": "{\\"mon\\": [9, 16], \\"tue\\": [9]}"}')

         ## add availability for employee2
        with boddle(method='POST', json={"job_id": job_record['id'],
                                         "employee_id": employee_record2['id'],
                                         "availability": {'mon': [10,15], 'tue': [14]}}):
            self.assertEqual(employee.post_employee_availability(db=self.db),
                '{"job_id": 1, "employee_id": 2, "availability": "{\\"mon\\": [10, 15], \\"tue\\": [14]}"}')


        ## add get match of employee and candidate avialability times
        with self.subTest(name="get availability of interview participants"):
            with boddle(method='GET'):
                result = job.get_attendee_availability(db=self.db, job_id=job_record['id'], candidate_id=candidate_record['id'])
                try:
                    self.assertEqual(json.loads(result), {"tue": [9], "mon": [9]})
                except json.decoder.JSONDecodeError:
                    self.assertEqual(result, "no matches found for candidate and interviewers")


if __name__ == '__main__':
    unittest.main()
