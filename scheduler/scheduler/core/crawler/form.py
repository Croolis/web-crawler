from .action import Action


class Form(Action):
    def __init__(self, status, page, selector, action):
        super().__init__('form', status, page)
        self.selector = selector
        self.action = action

    def __hash__(self):
        return hash((self.type, self.status, self.action))

    def __eq__(self, other):
        if not isinstance(other, Form):
            return False
        return self.type == other.type and self.status == other.status \
            and self.action == other.action
