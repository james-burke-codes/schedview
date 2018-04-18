#!env/bin/python3
import os
import sys
import builtins
import json
import logging
import argparse

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
    # setup logging
    logging.basicConfig(format=os.environ.get('SV_LOGGING_FORMAT'),
                        level=os.environ.get('SV_LOGGING_LEVEL'))
    # handle standalone service
    engine = create_engine(os.environ.get('SV_DB_CONNECTION'), echo=False)
    sqla_plugin = bottle_sqlalchemy.Plugin(engine, keyword="db")
    app.install(sqla_plugin)

    sys.path.append(os.path.dirname(os.path.realpath(__file__))+'/..')

import models
from models import Candidate, Interviewee


@app.route('/candidate', method=['OPTIONS', 'GET'])
def index(db):
    candidate = db.query(Candidate).all()
    return json.dumps([r.as_dict() for r in candidate], default=models.alchemyencoder)


@app.route('/candidate/:candidate_id', method=['OPTIONS', 'GET'])
def get_candidate(db, candidate_id=None):
    candidate = db.query(Candidate).filter(Candidate.id==candidate_id).first()
    return json.dumps(candidate.as_dict())


@app.route('/candidate/:candidate_id', method=['OPTIONS', 'PUT'])
def put_candidate(db, candidate_id=None):
    reqdata = request.json

    if request.content_type != "application/json":
        response.status = 400
        return "invalid request, expected header-content_type: application/json"

    candidate = db.query(Candidate).filter(Candidate.id==candidate_id).first()
    try:
        candidate.name = reqdata["name"]
        db.commit()
    except KeyError as e:
        logger.error(e)
        response.status = 400
        return "invalid request, no value for %s given" % e
    except sqlalchemy.exc.IntegrityError as e:
        logger.error(e)
        response.status = 400
        return str(e)

    return json.dumps(candidate.as_dict())


@app.route('/candidate', method=['OPTIONS', 'POST'])
def post_candidate(db):
    reqdata = request.json

    if request.content_type != "application/json":
        response.status = 400
        return "invalid request, expected header-content_type: application/json"

    try:
        candidate = Candidate(**reqdata)
        db.add(candidate)
        db.commit()
    except sqlalchemy.exc.IntegrityError as e:
        logger.error(e)
        response.status = 400
        return e
    return json.dumps(candidate.as_dict())


@app.route('/candidate/availability', method=['OPTIONS', 'PUT'])
def put_candidate_availability(db):
    reqdata = request.json

    if request.content_type != "application/json":
        response.status = 400
        return "invalid request, expected header-content_type: application/json"

    interviewee = db.query(Interviewee).filter(
        (Interviewee.job_id==reqdata["job_id"]) &
        (Interviewee.candidate_id==reqdata["candidate_id"])
        ).first()
    try:
        interviewee.availability=json.dumps(reqdata["availability"])
        db.commit()
        return json.dumps(interviewee.as_dict())
    except AssertionError as e:
        logger.error(e)
        response.status = 400
        return str(e)
    except sqlalchemy.exc.IntegrityError as e:
        logger.error(e)
        response.status = 400
        return e

    response.status = 400
    return "invalid request, could not locate Interviewee with those details"


@app.route('/candidate/availability', method=['OPTIONS', 'POST'])
def post_candidate_availability(db):
    reqdata = request.json

    if request.content_type != "application/json":
        response.status = 400
        return "invalid request, expected header-content_type: application/json"

    try:
        interviewee = Interviewee(job_id=reqdata["job_id"],
                                  candidate_id=reqdata["candidate_id"],
                                  availability=json.dumps(reqdata["availability"]))
        db.add(interviewee)
        db.commit()
    except AssertionError as e:
        logger.error(e)
        response.status = 400
        return str(e)
    except sqlalchemy.exc.IntegrityError as e:
        logger.error(e)
        response.status = 400
        return e

    return json.dumps(interviewee.as_dict())

