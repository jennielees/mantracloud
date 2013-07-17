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
from google.appengine.ext import db
from google.appengine.api import urlfetch
from datetime import datetime
import re


class Company(db.Model):
    ''' A class representing the Company structure in the CrunchBase API'''
    ''' We are only looking at overview, funding rounds, tags and description for now. '''
    
    permalink = db.StringProperty()
    name = db.StringProperty()
    overview = db.TextProperty()
    description = db.StringProperty(multiline=True)
    tags = db.StringListProperty()
        

class FundingRound(db.Model):
    ''' A class representing a funding round. '''
    ''' We care about when, from who and how much. '''
    round_code = db.StringProperty()
    raised_amount = db.IntegerProperty()
    raised_currency_code = db.StringProperty()
    funded_time = db.DateTimeProperty()
    company = db.ReferenceProperty(Company, collection_name='companies')    

class Word(db.Model):
   word = db.StringProperty()
   count = db.IntegerProperty()
   seen_in = db.StringListProperty()
   funding_data = db.StringListProperty()
   total_funding = db.IntegerProperty()
   source = db.StringProperty()
   fontsize = db.FloatProperty()

class WordMarker(db.Model):
    permalink = db.StringProperty()
        
class Api(object):
    ''' An API into CrunchBase. 
         Example usage:
             >>> import crunchbase
             >>> api = crunchbase.Api()
             >>> companies = api.GetAllCompanies()
             >>> company = api.GetCompany(name)
             
    '''
    total_companies = 0
    
    def GetTestCompany(self):
        aol = Company.all().filter('permalink =','zoho').get()
        return aol
    
    def GetAllCompanies(self):
        companies = Company.all().order('-name')
        return companies
    
    def SetAllCompanies(self,limit=None):
        chunk = 200
        start = int(limit)
        end = start+chunk
        url = 'http://api.crunchbase.com/v/1/companies.js'
        data = simplejson.loads(urlfetch.fetch(url).content)
        self.total_companies = len(data)
        newcompanylist = []
        smallerdata = data[start:start+chunk]
        for company in smallerdata:
                company_known = Company.get_by_key_name("p" + company['permalink'])
                if not company_known:
                    new_company = Company(permalink = company['permalink'],
                                      name = company['name'].strip(),
                                      key_name = "p" + company['permalink'])
                    newcompanylist.append(new_company)
        
        db.put(newcompanylist)
        # make sure the list is chunkable
        #i = 0
        #templist = []
        #while i < len(newcompanylist):
        #    print "Splitting: %s to %s" % (i, i+1500)
        #    print "======"
        #    templist = newcompanylist[i:i+1500]
        #    db.put(templist)
        #    print templist
        #    print "+++++++"
        #    i += 1500
        return end
    
    def UpdateCompanies(self, limit=None):
        chunk = 20
        start = int(limit)
        end = start + chunk
        
        url = 'http://api.crunchbase.com/v/1/companies.js'
        data = simplejson.loads(urlfetch.fetch(url).content)
        self.total_companies = len(data)
        newcompanylist = []
        smallerdata = data[start:start+chunk]
        for company in smallerdata:
                company_known = Company.get_by_key_name("p" + company['permalink'])
                to_put = self.SetCompanyData(company_known)
                newcompanylist.extend(to_put)
        db.put(newcompanylist)
        return end
    
    def UpdateCompaniesFromIterator(self, prev_key=None):
        chunk = 50
        
        #url = 'http://api.crunchbase.com/v/1/companies.js'
        #data = simplejson.loads(urlfetch.fetch(url).content)
        #self.total_companies = len(data)
        query = Company.all().order("permalink").filter("permalink >",prev_key).fetch(chunk)
        
        newcompanylist = []
        last_key = prev_key
        #smallerdata = data[start:start+chunk]
        for company in query:
                to_put = self.SetCompanyData(company)
                newcompanylist.extend(to_put)
                last_key = company.permalink
        db.put(newcompanylist)
        return last_key

    def SetCompanyByPermalink(self,permalink=None):
       company = Company.get_by_key_name("p" + permalink)
       to_put = self.SetCompanyData(company)
       db.put(to_put)
       return company
     
    def SetCompanyData(self, company=None):
       ''' http://api.crunchbase.com/v/1/<namespace>/<permalink>.js '''
       permalink = company.permalink
       companyURL = "http://api.crunchbase.com/v/1/company/" + permalink + ".js"
       data = simplejson.loads(urlfetch.fetch(companyURL).content)
       self.total_companies = len(data)
       company.overview = data['overview']
       company.description = data['description']
       if data['tag_list']:
        if data['tag_list'] != '':
          company.tags = data['tag_list'].split(",")
       putlist = []
       putlist.append(company)
       # db.put(company)
       
       funding_exist = FundingRound.all().filter("company =", company.key())
       db.delete(funding_exist)
       
       for deal in data['funding_rounds']:
        if deal['funded_month'] == None:
            deal['funded_month'] = '1'
        if deal['funded_year'] == None:
            deal['funded_year'] = '2005'
        if deal['raised_amount'] == None:
            deal['raised_amount'] = 0
        funding_round = FundingRound(company = company,
                                     round_code = deal['round_code'],
                                     raised_amount = int(deal['raised_amount']),
                                     raised_currency_code = deal['raised_currency_code'],
                                     funded_time = datetime.strptime("%s %s" % (deal['funded_month'], deal['funded_year']),"%m %Y"))
        #db.put(funding_round)
        putlist.append(funding_round)
       return putlist
    
    def GetCompanyFunded(self, company=None):
        rounds = FundingRound.all().filter("company =", company.key())
        return rounds
    
    def GetCompanyName(self, company=None):
        return company.name
    
    def GetNumberCompanies(self):
        return self.total_companies
    
    def remove_html_tags(self, data):
      p = re.compile(r'<.*?>')
      q = re.compile(r'[\.,";:]')
      return q.sub('', p.sub('', data))
    
    def CountWords(self,prev_key):
        chunk = 5
    
        # Get word marker from database
        marker = WordMarker.get_or_insert("countwords", permalink="0")
        permalink = marker.permalink
        
        query = Company.all().order("permalink").filter("permalink >",permalink).fetch(chunk)
        
        wordlist = []
        to_put_d = {}
        to_put = []
        last_key = prev_key
        stopwords = [ 'I', 'a', 'about', 'an', 'are', 'as', 'and', 'at', 'be', 'by', 'how', 'from', 'for', 'in', 'is',
                     'it', 'of', 'on', 'or', 'that', 'the', 'this', 'to', 'was', 'what', 'when', 'where',
                     'who', 'will', 'with', 'the', 'The', 'In', 'Our', 'our', 'also']

        #smallerdata = data[start:start+chunk]
        for company in query:
                # company.overview
                if company.overview:
                    overview_sp = self.remove_html_tags(company.overview).split()
                else:
                    overview_sp = ""
                if company.description: 
                    descr_sp = self.remove_html_tags(company.description).split()
                else:
                    descr_sp = ""
                for word in overview_sp:
                    if word not in stopwords:
                        if to_put_d.has_key(word):
                            word_model = to_put_d[word]
                        else:
                            word_model = Word.get_by_key_name("w" + word)
                        if not word_model:
                            # create new
                            word_model = Word(word = word,
                                             count = 1,
                                             seen_in = [ company.permalink ],
                                             source = 'overview',
                                             key_name = "w" + word)
                        else:
                            if company.permalink not in word_model.seen_in:
                              # update
                              word_model.count = word_model.count + 1
                              # print "updating %s with word %s's count of %s " % (company.permalink, word, word_model.count)
                              word_model.seen_in.append(company.permalink)
                        to_put_d[word] = word_model
                for word in descr_sp:
                    if word not in stopwords:
                        if to_put_d.has_key(word):
                            word_model = to_put_d[word]
                        else:
                            word_model = Word.get_by_key_name("w" + word)
                        if not word_model:
                            # create new
                            word_model = Word(word = word,
                                             count = 1,
                                             seen_in = [ company.permalink ],
                                             source = 'description',
                                             key_name = "w" + word)
                        else:
                            if company.permalink not in word_model.seen_in:
                              # update
                              word_model.count = word_model.count + 1
                              word_model.seen_in.append(company.permalink)
                        to_put_d[word] = word_model
                last_key = company.permalink
        # 500 requests at a time
        to_put = to_put_d.values()
        marker.permalink = last_key
        to_put.append(marker)
        i = 0
        while i < len(to_put):
            db.put(to_put[i:i+400])
            i += 400
        #db.put(to_put_d.values())
        return last_key
    
    def returnTopWords(self, number=50):
        # Return top -number- words
        
        stopwords = [ 'I', 'a', 'about', 'an', 'are', 'as', 'and', 'at', 'be', 'by', 'how', 'from', 'for', 'in', 'is',
                     'it', 'of', 'on', 'or', 'that', 'the', 'this', 'to', 'was', 'what', 'when', 'where',
                     'who', 'will', 'with', 'the', 'The', 'In', 'Our', 'our', 'also', 'has', 'its', 'which',
                     'their', 'they', 'company', 'them', 'It', 'can', 'over', 'up', 'They']
        query = Word.all().order("-count").fetch(number+len(stopwords))
        returnwords = []
        for word in query:
            if not word.word in stopwords:
                returnwords.append(word)
        return returnwords[0:number]
        