class Card:
    def __init__(self, front, back, tags=None):
        self.front = front
        self.back = back
        self.tags = [] if tags is None else tags

    def print_card_info(self):
        print("------------------------------------")
        print(f"Front: {self.front.strip()}")
        print(f"Back: {self.back.strip()}")
        print(f"Tags: {self.tags}")
        print("------------------------------------")
