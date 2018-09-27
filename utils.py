import logging
from googlesearch.googlesearch import GoogleSearch
import urllib2
from BeautifulSoup import BeautifulSoup
import urlparse
import os
import page
import heapq
import math
from url_normalize import url_normalize
import robotparser

import crawler

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
        logging.info("google returned link:: %s", result.url)
        urls.append(result.url)
    return urls


# fetches all url's present on a page
def get_links_on_page(url, html_page):
    soup = BeautifulSoup(html_page)
    links = []

    for link in soup.findAll('a', href=True):
        # logging.info("found link::%s", link['href'])
        url_in_page = link['href']
        try:
            if "https:" not in url_in_page or "http:" not in url_in_page:
                url_in_page = urlparse.urljoin(url, url_in_page)
            links.append(url_normalize(url_in_page))
        except UnicodeError:
            continue
    logging.info("found %d links on page %s", len(links), url)
    return links


# is_blacklisted_url accepts a list of blacklists and checks if those terms are present in the url
def is_blacklisted_url(blacklist, url):
    url = url.lower()
    for lookout in blacklist:
        if lookout in url:
            return True
    return False


# compute_relevance accepts an html page, search term and computes the relevance (0-100) for the search
def compute_relevance(html_page, search_term):
    relevance = 0
    for word in html_page.split():
        if word.lower() in search_term:
            relevance = relevance + 1

    if relevance < 100:
        return relevance
    return 100


# compute_promise takes a url and returns its predicted promise
def compute_promise(url_from, url_to, relevance, search_string):
    url_promise = 0
    for word in search_string.split():
        if word in url_to:
            url_promise = url_promise + 3
    if relevance[url_from]>0:
        return math.ceil(math.log(relevance[url_from])) + url_promise
    return url_promise


def update_url_promise(url, url_from, relevance, links, page_heap):
    index = page_heap.index(page.Page(url, 0, 0))
    crawled_page = page_heap[index]
    link_promise = relevance.get(url_from)
    number_of_links = len(links.get(url))
    new_promise = (((crawled_page.promise * number_of_links) + link_promise + math.log(number_of_links+1) - math.log(number_of_links))/(number_of_links+1))
    crawled_page.promise = new_promise
    if crawler.FOCUSSED_CRAWL:
        heapq.heapify(page_heap)
    links.get(url).append(url_from)


# can_crawl checks the domain of the url and returns true if it can be crawled
def can_crawl(url):
    try:
        url_split = urlparse.urlparse(url)
        robot_file_location = url_split.scheme+"://"+url_split.netloc+"/robots.txt"
        parser = robotparser.RobotFileParser()
        parser.set_url(robot_file_location)
        parser.read()
        return parser.can_fetch("*", url)
    except Exception:
        logging.error("unable to check robot.txt for :: %s ",url)
        return False













