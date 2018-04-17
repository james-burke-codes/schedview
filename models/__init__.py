from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from models.candidate import Candidate
from models.employee import Employee
from models.job import Job
from models.interviewer import Interviewer
from models.interviewee	import Interviewee

__all__ = [Candidate, Employee, Job, Interviewee, Interviewer]
