from .action import Action


class Link(Action):
    def __init__(self, link):
        super().__init__('link', 'p', link)

    def __hash__(self):
        return hash((self.type, self.status, self.page))

    def __eq__(self, other):
        if not isinstance(other, Link):
            return False
        return self.type == other.type and self.status == other.status and self.page == other.page
