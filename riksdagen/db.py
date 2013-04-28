# encoding: utf-8
from __future__ import unicode_literals
from collections import defaultdict, namedtuple

from sqlalchemy import Column, Unicode, ForeignKey, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
Session = sessionmaker()


class WorkingYear(Base):
    __tablename__ = 'working_years'
    id = Column(Unicode(7), primary_key=True)

    @classmethod
    def from_vote_json(cls, data):
        return cls(id=data['rm'])


class Constituency(Base):
    __tablename__ = 'constituencies'
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(Unicode(100))

    @classmethod
    def from_vote_json(cls, data):
        return cls(id=data['valkretsnummer'],
                   name=data['valkrets'])


class Person(Base):
    __tablename__ = 'people'
    id = Column(Unicode(32), primary_key=True)
    first_name = Column(Unicode(100))
    last_name = Column(Unicode(100))
    # Until a person in the riksdag has changed gender while there or
    # between two periods there I will just put this here.
    gender = Column(Unicode(6), default='Okänd')
    year_born = Column(Integer)

    @classmethod
    def from_vote_json(cls, data):
        return cls(id=data['intressent_id'],
                   first_name=data['fornamn'],
                   last_name=data['efternamn'],
                   gender=data['kon'],
                   year_born=data['fodd'])


class Votation(Base):
    __tablename__ = 'votations'
    id = Column(Unicode(36), primary_key=True)
    name = Column(Unicode(10))
    set_number = Column(Integer)
    votation = Column(Unicode(100))
    pertains_to = Column(Unicode(100))

    @classmethod
    def from_vote_json(cls, data):
        return cls(id=data['votering_id'],
                   name=data['beteckning'],
                   set_number=data['punkt'],
                   votation=data['votering'],
                   pertains_to=data['avser'])


class Vote(Base):
    __tablename__ = 'votes'
    votation_id = Column(Unicode(36), ForeignKey('votations.id'),
                         primary_key=True)
    person_id = Column(Unicode(32), ForeignKey('people.id'),
                       primary_key=True)
    constituency_id = Column(Integer, ForeignKey('constituencies.id'))
    vote = Column(Unicode(11), nullable=False)
    party = Column(Unicode(3), nullable=False)
    source = Column(Unicode(20), nullable=False)

    @classmethod
    def from_vote_json(cls, data):
        return cls(votation_id=data['votering_id'],
                   person_id=data['intressent_id'],
                   constituency_id=data['valkretsnummer'],
                   vote=data['rost'],
                   party=data['parti'],
                   source=data['källa'])


def add_votes(data, session):
    ModelMapping = namedtuple('ModelMapping', 'name key model')
    record_exists = defaultdict(lambda: set())
    models = [
        ModelMapping('working_year', 'rm', WorkingYear),
        ModelMapping('constituency', 'valkretsnummer', Constituency),
        ModelMapping('person', 'intressent_id', Person),
        ModelMapping('votation', 'votering_id', Votation),
    ]
    for i, row in enumerate(data):
        for model in models:
            if not row[model.key] in record_exists[model.name]:
                session.merge(model.model.from_vote_json(row))
                record_exists[model.name].add(row[model.key])

        session.merge(Vote.from_vote_json(row))
        if (i % 100) == 0: session.commit()
    session.commit()
