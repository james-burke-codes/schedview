
class MockSqlAlchemy(object):
    def __init__(self, count=0, *args, **kwargs):
        self.data = None
        self._count = count

    def __getattr__(self, *args, **kwargs):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def query(self, *args, **kwargs):
        # save the args passed to query - these are what we return
        self.data = args
        return self

    def all(self):
        # return the query args as a values/tuple of values in a list
        return [self.data]

    def first(self):
        # return the query args as a value/tuple of values
        return self.data if len(self.data) > 1 else self.data[0]

    def count(self):
        return self._count