#!env/bin/python3
import os
import sys
import builtins
import logging
import argparse

from configobj import ConfigObj
from validate import Validator

# SQLAlchemy
from bottle.ext import sqlalchemy as bottle_sqlalchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from bottle import Bottle

builtins.base = Base = declarative_base()

# import config
pathname = os.path.dirname(os.path.realpath(__file__))
configname = os.path.join(pathname, "config")
config = ConfigObj(configname+".conf", configspec=configname+".spec", interpolation=False)
config.validate(Validator())

# setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(format=config["logging"]["format"],
                    level=config["logging"]["level"])

app = application = Bottle()

# reference db in builtins - shares in-memory sqlite across apps
engine = create_engine(config["database"]["connection_string"], echo=True)
builtins.bottle_sqlalchemy = bottle_sqlalchemy.Plugin(engine,
                                                      builtins.base.metadata,
                                                      keyword="db",
                                                      create=True,
                                                      commit=True)
app.install(builtins.bottle_sqlalchemy)

# import apps
from candidate.service import app as canApp
app.merge(canApp)


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
