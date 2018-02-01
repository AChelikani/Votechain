class Transaction(object):
    def __init__(self, sender, receiver, value):
        self.sender = sender
        self.receiver = receiver
        self.value = value

    def to_json(self):
        return {
            "sender" : self.sender,
            "receiver" : self.receiver,
            "value" : self.value
        }
