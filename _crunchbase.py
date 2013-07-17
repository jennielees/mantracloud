#!/usr/bin/env python

# The CrunchBase API provides JSON representations of the data found on CrunchBase.
# http://groups.google.com/group/crunchbase-api/web/api-v1-documentation

# Copyright Jennie Lees
# jennie@affectlabs.com
# GNU GPL
# CrunchBase is a property of Techcrunch and I am in no way affiliated with it.
# Parts of this code were based on python-twitter by DeWitt@google.com.

'''A library that provides a Python interface to the CrunchBase API'''

__version__ = '0.1'
__author__ = 'jennie@affectlabs.com'

from django.utils import simplejson
import urllib

class Company(object):
    ''' A class representing the Company structure in the CrunchBase API'''
    ''' We are only looking at overview, funding rounds, tags and description for now. '''
    
    def __init__(self,
                 permalink=None,
                 name=None,
                 overview=None,
                 funded=None,
                 description=None,
                 tags=None):
        self.permalink = permalink
        self.name = name
        self.overview = overview
        self.funded = funded
        self.description = description
        self.tags = tags
        

class FundingRound(object):
    ''' A class representing a funding round. '''
    ''' We care about when, from who and how much. '''
    
    def __init__(self,
                 round_code=None,
                 raised_amount=None,
                 raised_currency_code=None,
                 funded_year=None,
                 funded_month=None):
        self.round_code = round_code
        self.raised_amount = raised_amount
        self.raised_currency_code = raised_currency_code
        self.funded_year = funded_year
        self.funded_month = funded_month
        
class Api(object):
    ''' An API into CrunchBase. 
         Example usage:
             >>> import crunchbase
             >>> api = crunchbase.Api()
             >>> companies = api.GetAllCompanies()
             >>> company = api.GetCompany(name)
             
    '''
    
    def GetAllCompanies(self):
        url = 'http://api.crunchbase.com/v/1/companies.js'
        data = simplejson.load(urllib.urlopen(url))
        for result in data:
            permalink = result['permalink']
            name = result['name']
            print permalink + name
    