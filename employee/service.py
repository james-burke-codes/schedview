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

logger = logging.getLogger(__name__)

app = application = Bottle()

try:
    app.install(builtins.bottle_sqlalchemy)
except AttributeError:
    # import config
    pathname = os.path.dirname(os.path.realpath(__file__))
    configname = os.path.join(pathname, "config")
    config = ConfigObj(configname+".conf", configspec=configname+".spec", interpolation=False)
    config.validate(Validator())

    # setup logging
    logging.basicConfig(format=config["logging"]["format"],
                        level=config["logging"]["level"])
    # handle standalone service
    engine = create_engine(config["database"]["connection_string"], echo=True)
    sqla_plugin = bottle_sqlalchemy.Plugin(engine, keyword="db")
    app.install(sqla_plugin)

    sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/..')

from models import Employee


@app.route('/employee', method=['OPTIONS', 'GET'])
def index(db):
    employees = db.query(Employee).all()
    return json.dumps([r.as_dict() for r in employees], default=builtins.alchemyencoder)


@app.route('/employee/:employee_id', method=['OPTIONS', 'GET'])
def get_employee(db, employee_id=None):
    employee = db.query(Employee).filter(Employee.id==employee_id).first()
    return json.dumps(employee.as_dict())


@app.route('/employee/:employee_id', method=['OPTIONS', 'PUT'])
def put_employee(db, employee_id=None):
    reqdata = request.json

    if request.content_type != "application/json":
        response.status = 400
        return {"status": "error", "message": "invalid request, expected header-content_type: application/json"}

    employee = db.query(Employee).filter(Employee.id==employee_id).first()
    try:
        employee.name = reqdata["name"]
        employee.title = reqdata["title"]
        employee.availability = reqdata["availability"]
        db.commit()
    except KeyError as e:
        logger.error(e)
        response.status = 400
        return e
    except sqlalchemy.exc.IntegrityError as e:
        logger.error(e)
        response.status = 400
        return e

    return json.dumps(employee.as_dict())

@app.route('/employee', method=['OPTIONS', 'POST'])
def post_employee(db):
    reqdata = request.json

    if request.content_type != "application/json":
        response.status = 400
        return {"status": "error", "message": "invalid request, expected header-content_type: application/json"}

    try:
        employee = Employee(**reqdata)
        db.add(employee)
        db.commit()
    except sqlalchemy.exc.IntegrityError as e:
        logger.error(e)
        response.status = 400
        return e
    return json.dumps(employee.as_dict())



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--listen", dest="listen", type=str, default="localhost", help="IP Address to listen on")
    parser.add_argument("-p", "--port", dest="port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("-d", "--debug", dest="bottleDebug", action="store_true", help="Enable Bottle debug mode")
    parser.set_defaults(bottleDebug=True)
    pargs = vars(parser.parse_args())
    app.run(host=pargs["listen"], port=pargs["port"], debug=pargs["bottleDebug"], reloader=True)