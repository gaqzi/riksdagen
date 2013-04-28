# encoding: utf-8
from __future__ import unicode_literals
import json
import unittest

from sqlalchemy import create_engine

from riksdagen import db


class TestDB(unittest.TestCase):
    def setUp(self):
        engine = create_engine('sqlite:///:memory:')
        # engine = create_engine('mysql://root@localhost/riksdagen?charset=utf8')
        self.connection = engine.connect()
        self.trans = self.connection.begin()

        db.Session.configure(bind=self.connection)
        self.session = db.Session()
        db.Base.metadata.create_all(engine)

        self.vote_data = {
            'votering_id': '75F2D01D-4EE1-11D7-AE75-006008577F08',
            'punkt': 7,
            'namn': 'Gunnar  Hökmark',
            'intressent_id': '0584386800218',
            'parti': 'm',
            'valkrets': 'Stockholms kommun',
            'valkretsnummer': 1,
            'iort': None,
            'rost': 'Nej',
            'avser': 'sakfrågan',
            'votering': 'huvud',
            'banknummer': 1,
            'fornamn': 'Gunnar',
            'efternamn': 'Hökmark',
            'kon': 'man',
            'fodd': 1952,
            'rm': '2002/03',
            'beteckning': 'UBU7',
            'källa': 'distribution'
        }

    def tearDown(self):
        self.trans.rollback()
        self.session.close()
        self.connection.close()

    def test_add_person(self):
        person = db.Person.from_vote_json(self.vote_data)
        self.session.add(person)
        self.session.commit()

        self.assertEqual(self.session.query(db.Person)
                         .filter(db.Person.id == '0584386800218').count(), 1)

    def test_add_person_ensure_m_w_for_gender(self):
        self.session.add(db.Person.from_vote_json(self.vote_data))

    def test_add_vote(self):
        db.add_votes([self.vote_data], self.session)
        for model in [db.WorkingYear, db.Constituency, db.Person,
                      db.Votation, db.Vote]:
            self.assertEqual(
                self.session.query(model).filter().count(), 1, model
            )

    def test_add_mass_votes(self):
        for file_name in ['75F2D01D-4EE1-11D7-AE75-006008577F08',
                          '75302AFA-9423-469E-8432-592DB4A4243F']:
            data = json.load(
                open('tests/fixtures/votation-{0}.json'.format(file_name)))
            if 'votering' in data: data = data['votering']['dokvotering']
            db.add_votes(data, self.session)

        self.longMessage = True
        session = self.session
        for model, expected in [(db.WorkingYear, 2),
                                (db.Constituency, 29),
                                (db.Person, 360),
                                (db.Votation, 2),
                                (db.Vote, 698)]:
            self.assertEqual(session.query(model).filter().count(), expected,
                             model)
