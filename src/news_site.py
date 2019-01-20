import urllib
import texttable
from enum import Enum
from googlesearch.googlesearch import GoogleSearch
from bs4 import BeautifulSoup
from textblob import TextBlob

class FetchType(Enum):
    DESCRIPTION = 1
    TEXT = 2
    NAME = 3

class NewsSite:

    def __init__(self, site_name, search_key, pages=1):
        self.site_name = site_name
        self.search_key = search_key
        self.search_depth = pages
        self.search_results_list = []
        self.search_links_list = []

    def google_search(self, fetch_type):
        search_results = GoogleSearch().search("inurl:" + self.site_name + " intext:" + self.search_key, num_results=self.search_depth)
        #search_results = google.search("inurl:" + self.site_name + " intext:" + self.search_key, pages=self.search_depth)
        for result in search_results:
            if fetch_type == FetchType.DESCRIPTION:
                search_results = result.description
            elif fetch_type == FetchType.NAME:
                search_results = result.name
            else:
                html = urllib.urlopen(result.link).read()
                search_results = self._clean_text(html)
            self.search_results_list.append(search_results)
            self.search_links_list.append(result.link)
        return [self.search_links_list, self.search_results_list]

    def analysis(self):
        subjectivity_list = []
        polarity_list = []

        for result in self.search_results_list:
            analysis = TextBlob(result)
            subjectivity = analysis.sentiment.subjectivity
            subjectivity_list.append(subjectivity)
            polarity = analysis.sentiment.polarity
            polarity_list.append(polarity)
        return [polarity_list, subjectivity_list]


    def _clean_text(html):
        soup = BeautifulSoup(html)

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out
        # get text
        text = soup.get_text()
        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n '.join(chunk for chunk in chunks if chunk)
        return text

    def createTable(self, link_list,subjectivity_list, polarity_list, detail=False):
        num = range(len(link_list))
        tab = texttable.Texttable(240)
        headings = ['Number','Results','Subjectivity', 'Polarity']
        tab.header(headings)

        for row in zip(num, link_list, subjectivity_list, polarity_list):
           tab.add_row(row)

        avg_subjectivity = (sum(subjectivity_list) / len(subjectivity_list))
        avg_polarity = (sum(polarity_list) / len(polarity_list))

        if detail:
            table = tab.draw()
        print(self.site_name)
        print(self.search_key)
        if detail:
            print (table)
        print (self.site_name + " average subjectivity: " + str(avg_subjectivity))
        print (self.site_name + " average polarity: " + str(avg_polarity))


def test():

    for site in ( "cnn.com", "newyorker.com","npr.com", "foxnews.com","drugdereport.com", "breitbart.com"):
        cnnObj = NewsSite(site ,"trump", 1)
        results = cnnObj.google_search(FetchType.DESCRIPTION)
        ana = cnnObj.analysis()
        cnnObj.createTable(results[0], ana[1], ana[0] )



test()