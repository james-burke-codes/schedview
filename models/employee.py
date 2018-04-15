import builtins

from sqlalchemy import *
from sqlalchemy.schema import *
from sqlalchemy.orm import *

from models import Base

class Employee(Base):
    __tablename__ = 'employee'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    availability = Column(String)


    def __init__(self, name, title, availability=None):
        self.name = name
        self.title = title
        self.availability = availability


    def __unicode__(self):
        return u'{self.name}'.format(self=self)


    def as_dict(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}