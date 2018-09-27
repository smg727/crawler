import utils
import heapq
import requests
import page
from urlparse import urlparse
import time

MAX_DEPTH_TO_CRAWL = 2
FOCUSSED_CRAWL = False
COSINE_RELEVANCE_THRESHOLD = 0.01


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
    if crawl_limit < 11:
        logger.error("no crawling required")
        return
    logger.info("starting search for %s by crawling %d pages", search_string, crawl_limit)

    # fetch initial pages
    logger.info("fetching initial seed links for :: %s",search_string)
    initial_urls = utils.fetch_seed(search_string)
    logger.info("%d initial seed links fetched", len(initial_urls))

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
    relevant_count = 0
    query_split = set(search_string.split())
    black_list = ["php","pdf", "jpg", "png", "mailto", "comment", "advertising", "javascript", "cite", "cite_note", "picture", "image", "photo", "#"]
    output_file = open("crawler.txt", "w");

    # push initial seed urls to heap
    for url in initial_urls:
        if FOCUSSED_CRAWL:
            heapq.heappush(page_heap, page.Page(url, 10, 0))
        else:
            page_heap.append(page.Page(url, 10, 0))
        links[url] = ["www.google.com"]

    # heapq.heappush(page_heap, page.Page("sangram",0,0))
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
        if FOCUSSED_CRAWL:
            next_page_to_crawl = heapq.heappop(page_heap)
        else:
            next_page_to_crawl = page_heap.pop(0)
        next_page_url = next_page_to_crawl.url

        try:
            if not utils.can_crawl(next_page_url):
                logger.info("not allowed to crawl %s", next_page_url)
                del links[next_page_url]
                continue
        except IOError:
            logger.error("error connecting to %s",next_page_url)
            continue
        try:
            logger.info("trying to fetch page :: %s", next_page_url)
            next_page = requests.get(next_page_url, timeout=1)
        except requests.exceptions.RequestException:
            logger.error("exception fetching page :: %s", next_page_url)
            continue
        if next_page.status_code != 200:
            logger.error("error fetching page :: %s", next_page.status_code)
            continue

        pages_crawled = pages_crawled + 1
        page_relevance = utils.compute_relevance(next_page.text, search_string)
        # scale cosine threshold to 0-100
        if page_relevance > COSINE_RELEVANCE_THRESHOLD*100:
            relevant_count = relevant_count + 1
        logger.info("the relevance of page %s was %d, promise was %d", next_page_url, page_relevance, next_page_to_crawl.promise)

        output_string = str(pages_crawled) + " the relevance of crawled page " + next_page_url + " was " +\
            str(page_relevance) + " promise was "+str(next_page_to_crawl.promise)+"\n"
        output_file.write(output_string)
        output_file.flush()

        relevance[next_page_url] = page_relevance
        old_domain = urlparse(next_page_url).netloc

        # if next_page_to_crawl.depth >= MAX_DEPTH_TO_CRAWL:
        #     logger.info("crawled too deep, not crawling page %s from domain %s", next_page_url, old_domain)
        #     continue

        links_on_page = utils.get_links_on_page(next_page_url, next_page.text)
        for url in links_on_page:
            # check if url has already been visited
            if url in relevance:
                logger.info("ignoring already visited url :: %s", url)
                continue
            # check if url is blacklisted
            if utils.is_blacklisted_url(black_list, url):
                logger.info("ignoring blacklisted url :: %s", url)
                continue
            # check if page is soon to be visited (page_heap)
            if page.Page(url, 0, 0) in page_heap:
                # update url promise, update new link
                logger.info("new pointer to %s , updating promise", url)
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
                continue
            predicted_promise = utils.compute_promise(next_page_url, url, relevance, search_string)
            new_page = page.Page(url, predicted_promise, depth)
            if FOCUSSED_CRAWL:
                heapq.heappush(page_heap, new_page)
            else:
                page_heap.append(new_page)
            links[url] = [next_page_url]

        del links[next_page_url]
    harvest_percentage = str(100*float(relevant_count)/float(crawl_limit))
    logger.info("harvest rate was "+harvest_percentage+" percent")
    output_file.close()


# heap-test
# list = []
# for i in range(0,10):
#     pg = page.Page("test", random.uniform(0, 100), 0)
#     heapq.heappush(list, pg)
#
# while len(list) > 0:
#     tmp = heapq.heappop(list)
#     print tmp.promise


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s minutes ---", ((time.time() - start_time)/60))

