from block import Block
from transaction import Transaction
import json
import hashlib
from flask import Flask, jsonify, request
from uuid import uuid4
import copy

class Blockchain(object):
    def __init__(self):
        self.blockchain = []
        self.next_block_transactions = [] # votes

        self.add_block(proof_of_work=100, previous_block_hash=1)

    def add_block(self, proof_of_work, previous_block_hash=None):
        block = Block(len(self.blockchain) + 1, self.next_block_transactions, proof_of_work, previous_block_hash or self.hash(self.blockchain[-1]))

        self.blockchain.append(block)
        self.next_block_transactions = []

        return block

    def add_transaction(self, sender, receiver, value):
        transaction = Transaction(sender, receiver, value)
        self.next_block_transactions.append(transaction)
        return self.get_last_block().index + 1

    def get_last_block(self):
        return self.blockchain[-1]

    def calculate_proof_of_work(self, last_proof):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof

        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    def to_json(self):
        blockchain = copy.deepcopy(self.blockchain)
        for x in range(len(blockchain)):
            blockchain[x] = blockchain[x].to_json()
        return blockchain

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the Proof: Does hash(last_proof, proof) contain 4 leading zeroes?

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :return: <bool> True if correct, False if not.
        """
        guess_string = str(last_proof) + str(proof)
        guess = guess_string.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def hash(block):
        hash_string = json.dumps(block.to_json(), sort_keys=True).encode()
        return hashlib.sha256(hash_string).hexdigest()

app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.get_last_block()
    last_proof = last_block.proof_of_work
    proof_of_work = blockchain.calculate_proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.add_transaction(
        sender="0",
        receiver=node_identifier,
        value=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.add_block(proof_of_work, previous_hash)

    transactions = copy.deepcopy(block.transactions)
    for x in range(len(transactions)):
        transactions[x] = transactions[x].to_json()

    response = {
        'message': "New Block Forged",
        'index': block.index,
        'transactions': transactions,
        'proof': block.proof_of_work,
        'previous_hash': block.previous_block_hash,
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'receiver', 'value']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.add_transaction(values['sender'], values['receiver'], values['value'])

    response = {'message': 'Transaction will be added to Block'}
    return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.to_json(),
        'length': len(blockchain.blockchain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
