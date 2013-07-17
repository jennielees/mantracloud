import os
import crunchbase

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db



class MainPage(webapp.RequestHandler):
   def get(self):
    #  api = crunchbase.Api()
      # api.SetAllCompanies()
    #  test_company = api.GetTestCompany()
    #  print test_company.name
    #  all_companies = api.GetAllCompanies()
      # Split these into 2 requests
    #  for company in all_companies:
    #     api.SetCompanyData(company)
    #     api.GetCompanyName(company)
    #     api.GetCompanyFunded(company)

    #  newtwitter = ''
    #  rounds = ''
    #  template_values = {
    #     'statuses' : all_companies,
    #     'rounds' : rounds,
    #  }
    
      api = crunchbase.Api()
      words = api.returnTopWords(75)

      maxFontSize = 18.0
      minFontSize = 8.0
      ratio = 1.0
      maxCount=float(words[0].count)
      minCount=float(words[-1].count)
      ratio = maxFontSize/(maxCount-minCount)

      for word in words:
#         if (ratio == 1.0):
#            maxCount = float(word.count)
#            ratio = maxFontSize/maxCount
         word.fontsize = minFontSize + (word.count * ratio)
    
      template_values = {
         'words' : words,
      }
          
      path = os.path.join(os.path.dirname(__file__), 'index.html')
      self.response.out.write(template.render(path, template_values))

class RefreshCompanies(webapp.RequestHandler):
   def get(self,args):
      api = crunchbase.Api()
      next = api.SetAllCompanies(args)
      number = api.GetNumberCompanies()
      
      template_values = {
         'next' : next,
         'total' : number,
         'url' : 'refreshlist',
      }
      
      path = os.path.join(os.path.dirname(__file__), 'list.html')
      self.response.out.write(template.render(path, template_values))
     
class UpdateCompanies(webapp.RequestHandler):
   def get(self,args):
      api = crunchbase.Api()
#      next = api.UpdateCompanies(args)
      next = api.UpdateCompaniesFromIterator(args)
      
      template_values = {
        'value' : next,
      }
      
      path = os.path.join(os.path.dirname(__file__), 'display_single.html')
      self.response.out.write(template.render(path, template_values))

class UpdateSingle(webapp.RequestHandler):
   def get(self,permalink):
      api = crunchbase.Api()
      company = api.SetCompanyByPermalink(permalink)
      print "%s done!" % company.name
      
class CountWords(webapp.RequestHandler):
   def get(self,permalink):
      api = crunchbase.Api()
      next = api.CountWords(permalink)
      
      template_values = {
        'value' : next,
      }
      
      path = os.path.join(os.path.dirname(__file__), 'display_single.html')
      self.response.out.write(template.render(path, template_values))

class WordsJSON(webapp.RequestHandler):
   def get(self):
      api = crunchbase.Api()
      words = api.returnTopWords()
      
      template_values = {
         'words' : words,
      }
      
      path = os.path.join(os.path.dirname(__file__), 'words_json.html')
      self.response.out.write(template.render(path, template_values))



class WordsXML(webapp.RequestHandler):
   def get(self):
      api = crunchbase.Api()
      words = api.returnTopWords()
      
      template_values = {
         'words' : words,
      }
      
      path = os.path.join(os.path.dirname(__file__), 'words_xml.html')
      self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/refreshlist/(.*)', RefreshCompanies),
                                      ('/update/(.*)', UpdateCompanies),
                                      ('/updatesingle/(.*)', UpdateSingle),
                                      ('/countwords/(.*)', CountWords),
                                      ('/json/words.json', WordsJSON),
                                      ('/xml/words.xml', WordsXML)
                                     ],
                                     debug=True)


def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()