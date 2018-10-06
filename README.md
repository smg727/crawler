# crawler
Crawler - A focussed web crawler
Sangram Ghuge
smg727@nyu.edu

The project consists of 3 main files:
1. page.py
2. utils.py
3. crawler.py


page.py
Page.py defines a class called page. Every link we crawl gets created into a page object and inserted into a page heap for tracking. Page class tracks the following:
url
promise
depth

utils.py
utils.py consists of helper functions called by the crawler. The functions defined here are:
setup_logging()
fetch_seed(search_term)
get_links_on_page(url, html_page)
is_blacklisted_url(blacklist, url)
compute_relevance(html_page, search_term)
compute_promise(url_from, url_to, relevance, search_string)
update_url_promise(url, url_from, relevance, links, page_heap, crawl_limit)
can_crawl(url)

crawler.py 
The logic behind running the crawler

venv 
Folder containing the virtual python environment and libraries

Logging:
When run the program writes a log of actions to crawler.log

Output:
When run the program writes stats about each page crawler to crawler.log

Execution:
The crawler runs by default on Focussed Mode.
Set the focussed_crawl flag to false to run in BFS mode.
The search query and number of pages to crawl are accepted as command line parameters

To understand the flow of the program let us first dive into the vital functions defined in utils.py:

setup_logging() : sets up logging for the program
fetch_seed(search_term): fetches the initial seed links from google
get_links_on_page(url, html_page): extracts all links on page
is_blacklisted_url(blacklist, url) : returns true if the url is blacklisted
compute_relevance(html_page, search_term): computes the relevance of a page using tf-idf vectors
compute_promise(url_from, url_to, relevance, search_string): computes the predicted promise of a page based on url and relevance of page we found url in 
update_url_promise(url, url_from, relevance, links, page_heap, crawl_limit): updates the promise of a page because we found a new page that links to the page and rebalances the heap
can_crawl(url): returns false if robot exclusion protocol prevents us from crawling to the page

Flow:
1. When the crawler starts it first fetches the seed pages from google.
2. These pages are added to either a queue(breath first search) or a heap of page objects(focussed search)
3. The heap of page objects is ordered with the page with the highest promise on top
4. We start a loop to crawl as many pages as listed
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
 

