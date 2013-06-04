# encoding: utf-8
from __future__ import unicode_literals
import json
import unittest

from testfixtures import LogCapture
from mock import MagicMock, patch

from riksdagen.api import (
    API_URL, votation_year, get_votation_ids, get_votation
)


class RequestsResponse(object):
    def __init__(self, data):
        self.data = data

    @property
    def text(self): return self.data

    def json(self): return json.loads(self.data)


class TestYearString(unittest.TestCase):
    def test_input_number(self):
        self.assertEqual(votation_year(2003), '2003/04')

    def test_input_string(self):
        self.assertEqual(votation_year('2004'), '2004/05')

    def test_input_string_already_has_slash_return_as_is(self):
        self.assertEqual(votation_year('2005/06'), '2005/06')

    def test_completely_unconforming_string_raises_ValueError(self):
        self.assertRaises(ValueError, votation_year, 'WellHelloThere')


class TestGetVotationIds(unittest.TestCase):
    def test_get_votation_ids_request_uri(self):
        mock = MagicMock(return_value=RequestsResponse('ok'))
        with patch('requests.get', mock):
            get_votation_ids(year=2003)

        mock.assert_called_with(
            '{0}/voteringlista/'.format(API_URL),
            params={'sz': 10000, 'utformat': 'iddump', 'rm': '2003/04'}
        )

    def test_get_votation_ids_parse_response(self):
        mock_votation_id = MagicMock(
            return_value=RequestsResponse(
                open('tests/fixtures/voteringsid-200304.csv').read()
            )
        )
        with patch('requests.get', mock_votation_id):
            votation_ids = get_votation_ids(year=2003)

        self.assertEqual(len(votation_ids), 642)
        self.assertEqual(votation_ids[0],
                         'C6F70B66-5EAA-11D7-AEF9-000475503871')
        self.assertEqual(votation_ids[-1],
                         '75F2D01D-4EE1-11D7-AE75-006008577F08')


class TestGetVotation(unittest.TestCase):
    def setUp(self):
        self.votation_id = '75F2D01D-4EE1-11D7-AE75-006008577F08'

    def test_get_data_request_uri(self):
        mock = MagicMock(return_value=RequestsResponse(
            '{"votering": {"dokvotering": []}}')
        )
        with patch('requests.get', mock):
            get_votation(self.votation_id)
        mock.assert_called_with(
            '{0}/votering/{1}/json'.format(API_URL, self.votation_id))

    def test_get_data_parse(self):
        mock = MagicMock(return_value=RequestsResponse(
            open('tests/fixtures/votation-{0}.json'.format(
                self.votation_id
            )).read()
        ))
        with patch('requests.get', mock):
            data = get_votation(self.votation_id)

        first_voter = data[0]
        self.assertEqual(first_voter['beteckning'], 'UBU7')
        self.assertEqual(first_voter['namn'], 'Gunnar  Hökmark')

    def test_invalid_json_document_returned(self):
        '''Shouldn't raise errors, log a message saying what went wrong'''
        mock = MagicMock(return_value=RequestsResponse(''))
        with LogCapture() as l:
            with patch('requests.get', mock):
                get_votation(self.votation_id)

            l.check(
                ('riksdagen', 'ERROR',
                 'Invalid JSON document for votation '
                 '"75F2D01D-4EE1-11D7-AE75-006008577F08".')
            )
