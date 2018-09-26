class Page:
    def __init__(self, url, promise=100, depth=0):
        self.url = url
        self.promise = promise
        self.depth = depth

    def __cmp__(self, other):
        return cmp(self.promise, other.promise)

    def __eq__(self, other):
        return self.url == other.url

