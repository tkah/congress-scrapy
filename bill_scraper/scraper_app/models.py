import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ARRAY, Text
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

def create_bills_table(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)

class Bills(DeclarativeBase):
    """Sqlalchemy bills model"""
    __tablename__ = "Bills"

    id = Column(String, primary_key=True)
    title = Column('title', Text)
    last_updated = Column('last_updated', DateTime)
    bill_number = Column('bill_number', String)
    congress = Column('congress', String)
    policy_area = Column('policy_area', ARRAY(String))
    subjects = Column('subjects', ARRAY(String))
    bill_type = Column('bill_type', String)
    summary = Column('summary', Text, nullable=True)
    cosponsor_ids = Column('cosponsor_ids', ARRAY(String))
    sponsor_ids = Column('sponsor_ids', ARRAY(String))
    actions = Column('actions', Text)
    related_bills = Column('related_bills', Text)
    created_at = Column('createdAt', DateTime, default=datetime.datetime.utcnow)
    updated_at = Column('updatedAt', DateTime, default=datetime.datetime.utcnow)
