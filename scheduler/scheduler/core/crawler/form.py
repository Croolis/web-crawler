from .action import Action


class Form(Action):
    def __init__(self, status, page, action, html_class):
        super().__init__('form', status, page)
        self.action = action
        self.html_class = html_class

    def __hash__(self):
        return hash((self.type, self.status, self.page, self.action))

    def __eq__(self, other):
        if not isinstance(other, Form):
            return False
        return self.type == other.type and self.status == other.status \
            and self.page == other.page and self.action == other.action
