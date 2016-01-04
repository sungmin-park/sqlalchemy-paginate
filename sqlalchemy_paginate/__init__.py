class Pagination(object):
    def __init__(self, query, page=1, per_page=10, per_nav=10,
                 map_=lambda x: x):
        self.total = query.count()
        if self.total == 0:
            self.last = 1
        else:
            self.last = self.total // per_page
            if self.total % per_page:
                self.last += 1
        self.page = max(min(self.last, page), 1)
