import utils
import heapq
import requests
import page
from urlparse import urlparse

LINKS_PER_PAGE = 10
MAX_DEPTH_TO_CRAWL = 2


def main():
    # setup logger
    logger = utils.setup_logging()
    logger.info("logger set up")

    # accept input
    search_string = raw_input("Enter search keyword ")
    try:
        crawl_limit = int(raw_input("Enter maximum number of pages to crawl "))
    except ValueError:
        logger.error("number of pages in not an integer")
        return
    if crawl_limit<11:
        logger.error("no crawling required")
        return
    logger.info("starting search for %s by crawling %d pages", search_string, crawl_limit)

    # fetch initial pages
    logger.info("fetching initial seed links for :: %s",search_string)
    initial_urls = utils.fetch_seed(search_string)
    logger.info("%d initial seed links fetched",len(initial_urls))

    # setup initial data

    # page_heap --> used to store type page which contains url, promise, depth
    # page_heap --> ordered by promise, largest promise on top
    page_heap = []
    # mapping to store relevance of crawled urls
    # url--> relevance
    relevance = {}
    # mapping to store incoming links from other urls
    # url -> [url1, url2...url_n]
    links = {}
    pages_crawled = 0
    black_list = ["pdf", "jpg", "png"]

    # push initial seed urls to heap
    for url in initial_urls:
        heapq.heappush(page_heap, page.Page(url, 100, 0))
        links[url] = ["www.google.com"]

    # setup loop to crawl the web
    # Flow:
    #   1. Pop page off the heap
    #   2. Fetch page
    #   3. Compute & store relevance
    #   4. If page was too deep, don't dig page for links
    #   5. Find all links in the page
    #   6. For all link
    #       1.  if we are seeing the url for the first time add to heap
    #       2. If we are seeing the url before, update promise in heap
    #   7. Repeat
    while pages_crawled < crawl_limit and len(page_heap) > 0:
        next_page_to_crawl = heapq.heappop(page_heap)
        next_page_url = next_page_to_crawl.url

        try:
            logger.info("trying to fetch page :: %s", next_page_url)
            next_page = requests.get(next_page_url)
        except requests.HTTPError:
            logger.error("exception fetching page :: %s", next_page_url)
            continue
        if next_page.status_code != 200:
            logger.error("error fetching page :: %s", next_page.status_code)
            continue

        page_relevance = utils.compute_relevance(next_page.text, search_string)
        logger.info("the relevance of page %s was %d", next_page_url, page_relevance)
        relevance[next_page_url] = page_relevance

        old_domain = urlparse(next_page_url).netloc

        links_on_page = utils.get_links_on_page(next_page_url, next_page.text)
        for url in links_on_page:
            # check if url has already been visited
            if url in relevance:
                logger.error("ignoring already visited url :: %s", url)
                continue
            # check if url is blacklisted
            if utils.is_blacklisted_url(black_list, url):
                logger.error("ignoring blacklisted url :: %s", url)
                continue
            # check if page is soon to be visited (page_heap)
            if page.Page(url, 0, 0) in page_heap:
                # update url promise, update new link
                logger.info("new pointer to %s , updating promise",url)
                utils.update_url_promise(url, next_page_url, relevance, links, page_heap)
                continue
            # At this point, we know we are seeing the page for the first time
            # add page to heap, create first link for page
            logger.info("new link %s found, adding to page_heap", url)

            new_domain = urlparse(url).netloc
            depth = 0
            if new_domain == old_domain:
                depth = next_page_to_crawl.depth + 1
            if depth >= MAX_DEPTH_TO_CRAWL:
                logger.info("crawled too deep, not crawling page %s from domain %s", url, new_domain)
                continue
            new_page = page.Page(url, relevance.get(next_page_url), depth)
            heapq.heappush(page_heap, new_page)
            links[url] = [next_page_url]

        del links[next_page_url]
        pages_crawled = pages_crawled + 1


if __name__ == "__main__":
    main()

