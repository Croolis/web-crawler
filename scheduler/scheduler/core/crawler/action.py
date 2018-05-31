class Action(object):
    def __init__(self, typ, status, page):
        self.type = typ
        self.status = status
        self.page = page
        self.url = None

    def __str__(self):
        return "{}, {}, {}".format(self.type, self.status, self.page)

    def __eq__(self, other):
        return self.type == other.type or self.status == other.status or self.page == other.page

    def __lt__(self, other):
        if not isinstance(other, Action):
            return False
        if self.type < other.type:
            return True
        if self.type == other.type and self.status < other.status:
            return True
        if self.type < other.type and self.status == other.status and self.page < other.page:
            return True
        return False
