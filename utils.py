import logging
from googlesearch.googlesearch import GoogleSearch
import urllib2
from BeautifulSoup import BeautifulSoup
import urlparse
import os
import requests
import random


# sets up the logging service.Logs are written to crawler.log
def setup_logging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='crawler.log',
                        filemode='w')

    return logging


# fetches the initial 11 results from google
def fetch_seed(search_term):
    try:
        response = GoogleSearch().search(search_term, num_results=11)
    except urllib2.HTTPError:
        logging.error("error fetching seed")
        os.exit(1)
    urls = list()
    for result in response.results:
        logging.info("google returned link:: %s",result.url)
        urls.append(result.url)
    return urls


# fetches all url's present on a page
def get_links_on_page(url):
    html_page = requests.get(url)
    soup = BeautifulSoup(html_page.text)
    links = []

    for link in soup.findAll('a', href=True):
        #logging.info("found link::%s", link['href'])
        url_in_page = link['href']
        if ":" not in url_in_page:
            url_in_page = urlparse.urljoin(url, url_in_page)
        links.append(url_in_page)
    logging.info("found %d links on page %s", len(links), url)
    return links


# is_blacklisted_url accepts a list of blacklists and checks if those terms are present in the url
def is_blacklisted_url(blacklist, url):
    for lookout in blacklist:
        if lookout in url:
            return False
    return True


# compute_relevance accepts an html page, search term and computes the relevance (0-100) for the search
def compute_relevance(html_page,search_term):
    return random.uniform(0, 100)


# compute_promise takes a url and returns its predicted promise
def compute_promise(url):
    return random.uniform(0, 100)







