import builtins
from sqlalchemy.ext.declarative import declarative_base

import models
builtins.models = models

Base = declarative_base()

from models.candidate import Candidate
from models.mockdb import MockSqlAlchemy

__all__ = [Candidate, MockSqlAlchemy]
