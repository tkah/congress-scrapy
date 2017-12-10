from sqlalchemy import create_engine, Column, Integer, String, DateTime, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

from .settings import DATABASE
DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL(**DATABASE))

def create_members_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)

class Members(DeclarativeBase):
    """Sqlalchemy members model"""
    __tablename__ = "members"

    id = Column(String, primary_key=True)
    party = Column('party', String)
    state = Column('state', String)
    phone = Column('phone', String)
    body = Column('body', String)
    last_name = Column('last_name', String)
    first_name = Column('first_name', String)
    district = Column('district', String)
    district_code = Column('district_code', String)
