import logging
from googlesearch.googlesearch import GoogleSearch
import urllib2
from BeautifulSoup import BeautifulSoup
import urlparse
import page
import heapq
import math
from url_normalize import url_normalize
import robotparser
from sklearn.feature_extraction.text import TfidfVectorizer
import crawler


# sets up the logging service.
# logs are written to crawler.log
def setup_logging():
    logging.basicConfig(level=logging.INFO,
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
    urls = list()
    for result in response.results:
        logging.info("google returned link:: %s", result.url)
        urls.append(result.url)
    return urls


# fetches all url's present on a page
def get_links_on_page(url, html_page):
    links = []

    try:
        soup = BeautifulSoup(html_page)
    except Exception:
        return links

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
    # transform the documents into tf-idf vectors
    vect = TfidfVectorizer(min_df=1)
    tfidf = vect.fit_transform([search_term, html_page])
    # compute the similarity between them
    similarity = (tfidf * tfidf.T).A
    doc_similarity = similarity[0][1]
    # value is in range 0-1 scale it 0-100
    return float(doc_similarity)*100


# compute_promise takes a url and returns its predicted promise
# this is called when we see a url for the first time
def compute_promise(url_from, url_to, relevance, search_string):
    url_promise = 0
    for word in search_string.split():
        if word in url_to:
            url_promise = url_promise + 3
    if relevance[url_from] > 0:
        return math.ceil(math.log(relevance[url_from])) + url_promise
    return url_promise


# update url promise is called when we see a link > 1
# it updates the promise based on the number of links pointing to url & their relevance's
def update_url_promise(url, url_from, relevance, links, page_heap, crawl_limit):
    # get page from the heap
    index = page_heap.index(page.Page(url, 0, 0))
    crawled_page = page_heap[index]
    # find current promise
    link_promise = relevance.get(url_from)
    number_of_links = len(links.get(url))

    # new promise is a weighted average of the relevance of links + log of the number of links pointing to it
    new_promise = (((crawled_page.promise * number_of_links) + link_promise + math.log(number_of_links+1) - math.log(number_of_links))/(number_of_links+1))
    crawled_page.promise = new_promise

    # heapify to get the updated promise to its correct ranking
    if crawler.FOCUSSED_CRAWL:
        heapq.heapify(page_heap)

    # an optimization to ensure heapify operation stays O(log(crawl_limit)
    if len(page_heap) > crawl_limit:
        logging.info("trimming heap")
        del page_heap[math.ceil(crawl_limit*0.8):]

    # update links graph with the new link
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













