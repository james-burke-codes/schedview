from sqlalchemy.ext.declarative import declarative_base
import datetime

def alchemyencoder(self, obj):
    """JSON encoder function for SQLAlchemy special classes."""
    if isinstance(obj, datetime.date):
        try:
            utcoffset = obj.utcoffset() or datetime.timedelta(0)
            return (obj - utcoffset).strftime('%Y-%m-%d %H:%M:%S')
        except AttributeError:
            return obj.strftime('%Y-%m-%d')
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

Base = declarative_base()

from models.candidate import Candidate
from models.employee import Employee
from models.job import Job
from models.interviewer import Interviewer
from models.interviewee	import Interviewee

__all__ = [Candidate, Employee, Job, Interviewee, Interviewer]
