class Action(object):
    def __init__(self, typ, status, page):
        self.type = typ
        self.status = status
        self.page = page
        self.url = None

    def __str__(self):
        return "{}, {}, {}".format(self.type, self.status, self.page)
