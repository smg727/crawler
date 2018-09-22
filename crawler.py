import utils
import heapq
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
    for url in initial_urls:
        heapq.heappush(page_heap, page.Page(url, 100, 0))
    # mapping to store relevance of crawled urls
    # url--> relevance
    relevance = {}
    # mapping to store incoming links from other urls
    # url -> [url1, url2...url_n]
    links = {}
    crawl_count = 0
    black_list = ["pdf", "jpg", "png"]

    linker = "https://www.youtube.com"
    print linker
    utils.get_links_on_page(linker)


if __name__ == "__main__":
    main()

