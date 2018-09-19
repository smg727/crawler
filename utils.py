import logging
from googlesearch.googlesearch import GoogleSearch


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
    response = GoogleSearch().search(search_term, num_results=11)
    urls = list()
    for result in response.results:
        urls.append(result.url)
    return urls





