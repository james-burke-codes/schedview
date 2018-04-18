#!env/bin/python3
import os
import sys
import builtins
import logging
import argparse

# SQLAlchemy
from bottle.ext import sqlalchemy as bottle_sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from bottle import Bottle
from models import Base

#builtins.base = Base = declarative_base()

# setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(format=os.environ.get('SV_LOGGING_FORMAT'),
                    level=os.environ.get('SV_LOGGING_LEVEL'))

app = application = Bottle()

# reference db in builtins - shares in-memory sqlite across apps
engine = create_engine(os.environ.get('SV_DB_CONNECTION'), echo=True)
builtins.bottle_sqlalchemy = bottle_sqlalchemy.Plugin(engine,
                                                      Base.metadata,
                                                      keyword="db",
                                                      create=True,
                                                      commit=True)
app.install(builtins.bottle_sqlalchemy)

# import apps
from candidate.candidate_service import app as canApp
from employee.employee_service import app as empApp
from job.job_service import app as jobApp
app.merge(canApp)
app.merge(empApp)
app.merge(jobApp)


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

builtins.alchemyencoder = alchemyencoder

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--listen", dest="listen", type=str, default="localhost", help="IP Address to listen on")
    parser.add_argument("-p", "--port", dest="port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("-d", "--debug", dest="debug", type=bool, default=True, help="Enable Bottle debug mode")
    pargs = vars(parser.parse_args())

    app.run(host=pargs["listen"], port=pargs["port"], debug=pargs["debug"], reloader=True)
