import os
import psycopg2
from .sql import SQL
from velocity.db.core import engine

default_config = {
    "database": os.environ["DBDatabase"],
    "host": os.environ["DBHost"],
    "port": os.environ["DBPort"],
    "user": os.environ["DBUser"],
    "password": os.environ["DBPassword"],
}


def initialize(config=None, **kwargs):
    if not config:
        config = default_config.copy()
    config.update(kwargs)
    return engine.Engine(psycopg2, config, SQL)
