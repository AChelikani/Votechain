from blockchain import Blockchain
import hashlib
import json
from time import time
from urlparse import urlparse
from uuid import uuid4
from block import Block
from transaction import Transaction

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain(100)


@app.route('/mine', methods=['GET'])
def mine():
    assert(len(blockchain.chain) < blockchain.num_voters)

    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)


    blockchain.add_transaction("0", node_identifier, 1)

    previous_hash = blockchain.hash(last_block)
    block = blockchain.add_block(proof, previous_hash)

    return jsonify(block.toJson()), 200


@app.route('/transactions/new', methods=['POST'])
def add_transaction():
    values = request.get_json()

    # Create a new Transaction
    index = blockchain.add_transaction(Transaction(values['sender'], values['recipient'], values['amount']))

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


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
