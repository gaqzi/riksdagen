# encoding: utf-8
import requests

API_URL = 'http://data.riksdagen.se'


# URI parameters from http://data.riksdagen.se/voteringlista/
# rm: Riksmöte
# bet: Beteckning
# punkt: Förslagspunkt
# parti: Parti
# valkrets: Valkrets
# rost: Röst (Avstår, Frånvarande, Ja, Nej
# iid: Ledamot
#
# Output format variables:
# sz: Antal utsvar (500, 2000, 10000)
# utformat: Utformat (HTML, xml, csv, iddump (All votation ids)
# gruppering: Gruppering (grouping)

def votation_year(year):
    ''' Takes a year and return it in the format required by Riksdagens API.
    The format is: <current_year_4_digits>/<following_year_two_digits>.

    Arguments:
      year: A year as an integer or as a string

    Returns:
      string: <year>/<following_year_two_digits>
    '''
    try:
        year = int(year)
    except ValueError:
        if '/' in year: return year
        raise

    years_to_remove = 2000
    if year < 2000: years_to_remove = 1900

    return '{0}/{1:02d}'.format(year, (year - years_to_remove) + 1)


def get_votation_ids(year=None):
    '''Returns a list of votation ids for the given year or current
    year if none passed.

    Arguments:
      year: A year that corresponds to the votation year format

    Returns:
      A list of votation ids
    '''
    params = dict(
        sz=10000,
        utformat='iddump'
    )
    if year: params['rm'] = votation_year(year)

    r = requests.get('{0}/voteringlista/'.format(API_URL), params=params)
    return r.text.split(',')


def get_votation(id):
    ''' Returns a list of dicts which corresponds to a votation.

    Arguments:
      id: A votation id

    Returns:
      A list of dicts that represents a vote in the votation
    '''
    r = requests.get('{0}/votering/{1}/json'.format(API_URL, id))

    return r.json()['votering']['dokvotering']
