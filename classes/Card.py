class Card:
    def __init__(self, forward="", backward="", source="", tags=None):
        self.forward = forward
        self.backward = backward
        self.source = source
        self.tags = [] if tags is None else tags
