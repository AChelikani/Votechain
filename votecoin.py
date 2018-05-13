from blockchain import Blockchain
import hashlib
import json
from time import time
from urlparse import urlparse
from uuid import uuid4
from block import Block
from transaction import Transaction
import random
from wallet import Wallet

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

# Initialize blockchain with 100 voters (100 coins)
blockchain = Blockchain(100)


@app.route('/mine', methods=['GET'])
def mine():
    assert(len(blockchain.chain) < blockchain.num_voters)

    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)


    blockchain.add_transaction("0", node_identifier, 1)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.add_block(proof, previous_hash)

    return jsonify(block.to_json()), 200


@app.route('/transactions/new', methods=['POST'])
def add_transaction():
    values = request.get_json()

    # Create a new Transaction
    index = blockchain.add_transaction(Transaction(values['sender'], values['receiver'], values['amount']))

    response = {'message': 'Transaction will be added to Block ' + str(index)}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def chain():
    blockchain_chain = []
    for block in blockchain.chain:
        blockchain_chain.append(block.to_json())

    response = {
        'chain': blockchain_chain,
        'length': len(blockchain_chain),
    }
    return jsonify(response), 200

@app.route('/nodes/resolve', methods=['GET'])
def consensus_protocol():
    replaced = blockchain.resolve_conflicts()
    blockchain_chain = blockchain.to_json()
    if replaced:
        response = {
            'message': 'Chain replaced',
            'new_chain': blockchain_chain
        }
    else:
        response = {
            'message': 'Chain kept',
            'chain': blockchain_chain
        }

    return jsonify(response), 200

@app.route('/vote', methods=['GET'])
def vote():
    # Setup wallets for both of the candidates
    candidate1 = Wallet("Candidate 1")
    candidate2 = Wallet("Candidate 2")

    # Two candidates, each coin randomly votes for a candidate
    num_coins = len(blockchain.chain)
    votes = []
    for x in range(num_coins):
        votes.append(random.randint(1,2))
    result = "<h1> Votes </h1>"
    for x in range(len(votes)):
        result += "<p> voter " + str(x+1) + " voted for candidate " + str(votes[x]) + " </p>"
        if votes[x] == 1:
            candidate1.add_money(1)
        elif votes[x] == 2:
            candidate2.add_money(2)
    result += "<br>"
    result += "Candidate 1 total votes: " + str(candidate1.get_total())
    result += "Candidate 2 total votes: " + str(candidate2.get_total())
    #transaction = Transaction(sender, receiver, 1)
    return result



'''
@app.route('/visualize', methods=['GET'])
def visualize():
    output = "Blockchain: \n"
    blockchain_chain = []
    for block in blockchain.chain:
        blockchain_chain.append(block.to_json())
    chain = blockchain_chain
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
