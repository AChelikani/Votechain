class Wallet:
    def __init__(self, name):
        self.owner = name
        self.total = 0.0

    def add_money(self, amount):
        self.total += amount

    def get_total(self):
        return self.total
