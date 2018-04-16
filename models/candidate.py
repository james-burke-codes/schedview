import builtins
import json

from sqlalchemy import *
from sqlalchemy.schema import *
from sqlalchemy.orm import *

from models import Base

class Candidate(Base):
    __tablename__ = 'candidate'

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    availability = Column(String)

    def __init__(self, name, availability=json.dumps(dict())):
        self.name = name
        self.availability = availability


    def __unicode__(self):
        return u'{self.name}'.format(self=self)


    def as_dict(self):
        return {c: getattr(self, c) for c in inspect(self).attrs.keys()}


    @validates('availability')
    def validate_address(self, key, availability):
        if availability and json.loads(availability):
            assert json.loads(availability)
            assert set(json.loads(availability).keys()).issubset(set(('mon', 'tue', 'wed', 'thur', 'fri')))
        return availability