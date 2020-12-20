class Card:
    def __init__(self, front, back, tags=None):
        self.front = front
        self.back = back
        self.tags = [] if tags is None else tags
