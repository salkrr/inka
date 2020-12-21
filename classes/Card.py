class Card:
    def __init__(self, front, back, tags=None):
        self.front_raw = front
        self.back_raw = back
        self.front_converted = None
        self.back_converted = None
        self.tags = [] if tags is None else tags

    def print_card_info(self):
        print("------------------------------------")
        print(f"Front: {self.front_raw.strip()}")
        print(f"Back: {self.back_raw.strip()}")
        print(f"Tags: {self.tags}")
        print("------------------------------------")
