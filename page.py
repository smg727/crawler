class Page:
    def __init__(self, url, promise=100, depth=0):
        self.url = url
        self.promise = promise
        self.depth = depth

    def __lt__(self, other):
        return cmp(self.promise, other.promise)

