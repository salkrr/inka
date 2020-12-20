class Card:
    def __init__(self, forward="", backward="", tags=None):
        self.forward = forward
        self.backward = backward
        self.tags = [] if tags is None else tags
