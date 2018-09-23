import utils
import heapq
import requests
import page

LINKS_PER_PAGE = 10


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
    initial_urls = utils.fetch_seed(search_string)
    logger.info("initial seed links fetched")

    # setup initial data
    page_heap = []
    # mapping to store relevance of crawled urls
    # url--> relevance
    relevance = {}
    # mapping to store incoming links from other urls
    # url -> [url1, url2...url_n]
    links = {}
    pages_crawled = 0
    black_list = ["pdf", "jpg", "png"]
    for url in initial_urls:
        heapq.heappush(page_heap, page.Page(url, 100, 0))
        links[url] = ["www.google.com"]

    while pages_crawled < crawl_limit and len(page_heap) > 0:
        next_page = heapq.heappop(page_heap)
        next_page_url = next_page.url

        try:
            logger.info("trying to get page :: %s", next_page_url)
            next_page = requests.get(next_page_url)
        except requests.HTTPError:
            logger.error("exception fetching page :: %s", next_page_url)
            continue
        if next_page.status_code != 200:
            logger.error("error fetching page :: %s", next_page.status_code)
            continue

        page_relevance = utils.compute_relevance(next_page.text, search_string)
        relevance[next_page_url] = page_relevance

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
            logger.info("new link %s found, adding to page_heap",url)
            new_page = page.Page(url, relevance.get(next_page_url), 0)
            heapq.heappush(page_heap, new_page)
            links[url] = [next_page_url]
            # TODO: find new depth by checking if it is the same domain

        del links[next_page_url]


if __name__ == "__main__":
    main()

