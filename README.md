# schedview

[![Build Status](https://travis-ci.org/peregrinius/schedview.svg?branch=master)](https://travis-ci.org/peregrinius/schedview) [![codecov](https://codecov.io/gh/peregrinius/schedview/branch/master/graph/badge.svg)](https://codecov.io/gh/peregrinius/schedview)

Schedview is a Web API for managing interview timeslots between candidates and employees


## Installation

```
git clone git@github.com:peregrinius/schedview.git

cd schedview
virtualenv -p <path to python3> venv
source venv/bin/activate

pip install requirements.txt
```

## Testing

```
pytest

```

## Running

```
python run.py
```

## Development

Schedview is built using the Bottle Python Web Framework, each application is separate and can be run independently, while also being able to run together using the `python run.py` command.


## Data Model

There is a many to many relationship between a candidate and a job and between an employee and a job. This means that a candidate can apply for many jobs and an employee can interview many candidates and many employees can interview the same candidate.

```
+-----------+        +-----+        +-----------+
|INTERVIEWEE+^-------+ JOB +-------^+INTERVIEWER|
+-----+-----+        +-----+        +-----+-----+
      ^                                   ^
      |                                   |
+-----+----+                         +----+----+
|CANDIDATE |                         |EMPLOYEE |
+----------+                         +---------+
```


## To Do

- Create constraint on Interviewee table to prevent a candidate from applying for the same job multiple times.
- Add more tests to check failures e.g. sending candidate_id to employee get
