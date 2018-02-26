class Transaction(object):
    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def to_json(self):
        return {
            "sender" : self.sender,
            "receiver" : self.receiver,
            "amount" : self.amount
        }
