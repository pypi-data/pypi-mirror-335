"""Functions for connecting to and populating the course database"""
import os
import psycopg2
from sqlalchemy import create_engine

from .data import (
    load_diamonds,
    load_movies,
)


def populate_database():
    """Populate the database with the diamonds data
    """
    diamonds = load_diamonds()
    movies = load_movies()
    db = create_sqlalchemy_engine()
    with db.connect() as connection:
        diamonds.to_sql(
            "diamonds",
            con=connection,
            if_exists="replace",
            index=False
        )
        movies.to_sql(
            "movies",
            con=connection,
            if_exists="replace",
            index=False
        )
        connection.commit()  # save the changes


def create_sqlalchemy_engine():
    """Connect to the course database with SQLAlchemy

    :return:
    sqlalchemy.engine.Engine object for database connectivity
    """
    connection_string = get_connection_string()
    return create_engine(connection_string)


def connect_to_database():
    """Connect to the course database with psycopg2

    :return:
    psycopg2 connection object
    """
    connection_string = get_connection_string()
    return psycopg2.connect(connection_string)


def get_connection_string() -> str:
    """Obtain the connection string for the course database

    :return:
    String with the database, host and user info
    """
    # Use environment variables in GitLab, defaults otherwise
    user = os.getenv("POSTGRES_USER", "jr")
    password = os.getenv("POSTGRES_PASSWORD", "jr-pass")
    hostname = os.getenv("POSTGRES_HOSTNAME", "localhost")
    db = os.getenv("POSTGRES_DB", "test")
    return f"postgresql://{user}:{password}@{hostname}/{db}"
