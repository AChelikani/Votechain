import time
import copy

class Block(object):
    def __init__(self, index, transactions, proof_of_work, previous_block_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.proof_of_work = proof_of_work
        self.previous_block_hash = previous_block_hash

    def to_json(self):
        transactions = copy.deepcopy(self.transactions)
        for x in range(len(transactions)):
            print transactions[x]
            transactions[x] = transactions[x].to_json()

        return {
            "index" : self.index,
            "timestamp" : self.timestamp,
            "transactions" : transactions,
            "proof_of_work" : self.proof_of_work,
            "previous_block_hash" : self.previous_block_hash
        }
