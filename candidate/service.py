import os
import sys
import builtins
import json
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
from bottle import request, response
import sqlalchemy

# import config
pathname = os.path.dirname(os.path.realpath(__file__)) + '/../'
configname = os.path.join(pathname, "config")
config = ConfigObj(configname+".conf", configspec=configname+".spec", interpolation=False)
config.validate(Validator())

# setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(format=config["logging"]["format"],
                    level=config["logging"]["level"])

app = application = Bottle()


try:
    app.install(builtins.bottle_sqlalchemy)
except AttributeError:
    # handle standalone service
    engine = create_engine(config["database"]["connection_string"], echo=True)
    sqla_plugin = bottle_sqlalchemy.Plugin(engine, keyword="db")
    app.install(sqla_plugin)

    # TODO - add support for models


@app.route('/candidate', method=['OPTIONS', 'GET'])
def index(db):
    candidate = db.query(models.Candidate).all()
    return json.dumps([r.as_dict() for r in candidate], default=builtins.alchemyencoder)



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--listen", dest="listen", type=str, default="localhost", help="IP Address to listen on")
    parser.add_argument("-p", "--port", dest="port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("-d", "--debug", dest="bottleDebug", action="store_true", help="Enable Bottle debug mode")
    parser.set_defaults(bottleDebug=True)
    pargs = vars(parser.parse_args())
    app.run(host=pargs["listen"], port=pargs["port"], debug=pargs["bottleDebug"], reloader=True)
