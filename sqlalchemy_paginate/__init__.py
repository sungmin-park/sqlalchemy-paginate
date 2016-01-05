def int_ceil(x, y):
    """
    equivalent to math.ceil(x / y)
    :param x:
    :param y:
    :return:
    """
    q, r = divmod(x, y)
    if r:
        q += 1
    return q


class Pagination(object):
    def __init__(self, query, page=1, per_page=10, per_nav=10,
                 map_=lambda x: x):
        self.first = 1
        self.total = query.count()
        if self.total == 0:
            self.last = 1
        else:
            self.last = int_ceil(self.total, per_page)
        self.page = max(min(self.last, page), 1)

        self.prev = max(self.page - 1, 1)
        self.has_prev = self.prev != self.page
        self.next = min(self.page + 1, self.last)
        self.has_next = self.next != self.page

        self.nav_head = per_nav * (int_ceil(self.page, per_nav) - 1) + 1
        self.nav_tail = min(self.last, self.nav_head + per_nav - 1)

        self.nav_prev = max(self.page - per_nav, 1)
        self.has_nav_prev = self.nav_prev < self.nav_head
        self.nav_next = min(self.page + per_nav, self.last)
        self.has_nav_next = self.nav_next > self.nav_tail

        self.pages = range(self.nav_head, self.nav_tail + 1)

        start = (self.page - 1) * per_page
        self.items = map(map_, query[start: start + per_page])
