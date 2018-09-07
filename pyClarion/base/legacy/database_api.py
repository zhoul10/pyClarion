from __future__ import absolute_import

# Clarion Architecture implementation in Python.
# Copyright (C) 2013-2014 Clarion-Architecture Authors (see AUTHORS.txt)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>. 

__author__ = 'Mike'

import sys
import os
import json
import random
import time
import logging
import pprint
import sqlalchemy

from clarion.core import dimension

# Uncomment to help debug problems with the path
# print(sys.path)

logger = logging.getLogger(__name__)

def create_postgresql_session(username, password, hostname, database):
    """
    Creates and returns a session for the given postgresql database using sqlalchemy.
    """
    logger.info("Creating postgresql session.")
    engine = sqlalchemy.create_engine(
        "".join(["postgresql://", username, ":", password, "@", hostname, "/", database]))
    dimension.Base.metadata.create_all(engine)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    return Session()

def create_postgresql_connection(username, password, hostname, database):
    """
    Creates and returns a connection to the database.
    """
    logger.info("Creating postgresql connection.")
    engine = sqlalchemy.create_engine(
        "".join(["postgresql://", username, ":", password, "@", hostname, "/", database]))
    return engine.connect()

def postgresql_database_exists(username, password, hostname, database):
    """
    Checks if a database exists in postgresql.
    Returns True if it exists; False otherwise.
    """
    logger.info("Checking for database.")
    engine = sqlalchemy.create_engine(
        "".join(["postgresql://", username, ":", password, "@", hostname, "/postgres"]))
    conn = engine.connect()
    try:
        result = conn.execute("".join(["SELECT 1 FROM pg_database WHERE datname = \'", database, "\'"]))
        if result.first():
            logger.info("Database exists.")
            return True
        logger.info("Database does not exist.")
        return False
    except:
        logger.error("Error checking for database.")
        conn.close()
        return False

def create_postgresql_database(username, password, hostname, database):
    """
    Ensures the creation of a postgresql database.
    """
    logger.info("Creating postgresql database.")
    engine = sqlalchemy.create_engine(
        "".join(["postgresql://", username, ":", password, "@", hostname, "/postgres"]))
    conn = engine.connect()
    try:
        conn.execute("commit")
        conn.execute("".join(["create database ", database]))
        conn.close()
        logger.info("Postgresql database created.")
    except:
        conn.close()
        logger.error("Error creating database.")

def drop_postgresql_database(username, password, hostname, database):
    """
    Drops the given postgresql database.
    """
    logger.info("Dropping postgresql database.")
    engine = sqlalchemy.create_engine(
        "".join(["postgresql://", username, ":", password, "@", hostname, "/postgres"]))
    conn = engine.connect()
    try:
        conn.execute("commit")
        conn.execute("".join(["drop database ", database]))
        conn.close()
        logger.info("Postgresql database dropped.")
    except sqlalchemy.exc.ProgrammingError:
        conn.close()
        logger.error("Error dropping database.")

def reset_postgresql_database(username, password, hostname, database):
    drop_postgresql_database(username, password, hostname, database)
    create_postgresql_database(username, password, hostname, database)

def validate_postgresql_database(username, password, hostname, database, jcontext):
    """
    Validates the existing database with the given json context.
    """
    # TODO: Write this
    # Possibly move this elsewhere?
    pass
