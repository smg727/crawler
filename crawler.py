import utils
import heapq
import page


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

    # setup initial data
    page_heap = []
    for url in initial_urls:
        heapq.heappush(page_heap, page.Page(url, 100, 0))
    # while len(page_heap) > 0:
    #     element = heapq.heappop(page_heap)
    #     print element.url


if __name__ == "__main__":
    main()

