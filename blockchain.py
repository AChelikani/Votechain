import hashlib
import json
from time import time
from urlparse import urlparse
from uuid import uuid4
from block import Block
from transaction import Transaction

import requests
from flask import Flask, jsonify, request


class Blockchain:
    def __init__(self, num_voters):
        self.current_transactions = []
        self.chain = []
        # Set of all nodes accessing miner
        self.nodes = set()
        self.num_voters = num_voters

        # Original block
        self.add_block(previous_hash='1', proof=100)

    def register_node(self, address):
        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def valid_chain(self, chain):
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            if block['previous_hash'] != self.hash(last_block):
                return False

            if not self.valid_proof(last_block['proof'], block['proof'], last_block['previous_hash']):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        # This is in case of a conflict chain copy mined by a rogue party
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)

        for node in neighbours:
            response = requests.get('http://' + node + '/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

    def add_block(self, proof, previous_hash):
        block = Block(len(self.chain) + 1, self.current_transactions, proof, previous_hash or self.hash(self.chain[-1]))

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def add_transaction(self, sender, receiver, amount):
        transaction = Transaction(sender, receiver, amount)

        self.current_transactions.append(transaction)

        return self.last_block.index + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):

        block_string = json.dumps(block.to_json(), sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        last_proof = last_block.proof_of_work
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        guess = str(last_proof) + str(proof) + last_hash
        guess_hash = hashlib.sha256(guess.encode()).hexdigest()
        return guess_hash[:4] == "0000"

    def to_json(self):
        blockchain_chain = []
        for block in blockchain:
            blockchain_chain.append(block.to_json())
        return blockchain_chain
