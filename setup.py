# encoding: utf-8
from setuptools import setup

setup(
    name='riksdagen-voteringsdatabas',
    version='0.1',
    description='Fetch votations and votes from Riksdagens API',
    author=u'Björn Andersson',
    author_email='ba@sanitarium.se',
    url='https://github.com/gaqzi/riksdagen/',
    license='BSD',
    scripts=['bin/riksdagen'],
    packages=['riksdagen'],
    install_requires=[
        'SQLAlchemy==0.8.1',
        'requests==1.2.0',
        'progressbar==2.3',
    ],
    test_suite='nose.collector',
    tests_require=['nose>=1.3.0'],
)
