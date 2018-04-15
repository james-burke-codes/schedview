import builtins
from sqlalchemy.ext.declarative import declarative_base

import models
builtins.models = models

try:
    Base = builtins.base
except AttributeError:
	Base = declarative_base()

from models.candidate import Candidate
from models.employee import Employee

__all__ = [Candidate, Employee]
