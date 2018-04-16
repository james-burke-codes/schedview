from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from models.candidate import Candidate
from models.employee import Employee

__all__ = [Candidate, Employee]
