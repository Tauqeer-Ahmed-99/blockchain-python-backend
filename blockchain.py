from collections import OrderedDict
import json
from functools import reduce
from time import time

import requests

from utility.utils import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet


class Blockchain:
    MINING_REWARD = 10.00

    def __init__(self, public_key, uid):
        GENESIS_BLOCK = Block(0, "", [], 100, 0)
        self.blockchain = [GENESIS_BLOCK]
        self.open_transactions = []
        self.public_key = public_key
        self.peer_nodes = set()
        self.resolve_conflicts = False
        self.uid = uid
        self.load_data()

    def load_data(self):
        try:
            with open(f"blockchain-{self.uid}.txt", mode="r") as file:
                file_content = file.readlines()
                blockchain = json.loads(file_content[0][:-1])
                updated_blockchain = []
                for block in blockchain:
                    loaded_transactions = [Transaction(
                        tx["sender"], tx["recipient"], tx["amount"], tx["signature"]) for tx in block["transactions"]]
                    loaded_block = Block(
                        block["index"], block["previous_hash"], loaded_transactions, block["proof"], block["time"])
                    updated_blockchain.append(loaded_block)
                self.blockchain = updated_blockchain

                open_transactions = json.loads(file_content[1][:-1])
                updated_open_transations = []
                for tx in open_transactions:
                    loaded_transaction = Transaction(
                        tx["sender"], tx["recipient"], tx["amount"], tx["signature"])
                    updated_open_transations.append(loaded_transaction)
                self.open_transactions = updated_open_transations

                peer_nodes = json.loads(file_content[2])
                self.peer_nodes = set(peer_nodes)

        except (IOError, IndexError):
            pass

    def save_data(self):
        try:
            with open(f"blockchain-{self.uid}.txt", mode="w") as file:
                saveable_data = [block.__dict__ for block in [Block(
                    block_el.index,
                    block_el.previous_hash,
                    [tx.__dict__ for tx in block_el.transactions],
                    block_el.proof,
                    block_el.time) for block_el in self.blockchain]]
                file.write(json.dumps(saveable_data))
                file.write("\n")
                saveable_open_transactions = [
                    tx.__dict__ for tx in self.open_transactions]
                file.write(json.dumps(saveable_open_transactions))
                file.write("\n")
                file.write(json.dumps(list(self.peer_nodes)))

        except IOError:
            print("Saving data failed!!!")

    def proof_of_work(self):
        last_block = self.blockchain[-1]
        hashed_last_block = hash_block(last_block)
        proof = 1
        while not Verification.validate_proof(
            self.open_transactions,
            hashed_last_block,
            proof
        ):
            proof += 1
        return proof

    def get_balance(self, user=None):
        if user is None:
            if self.public_key is None:
                return None
            participant = self.public_key
        else:
            participant = user

        # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of transactions that were already included in blocks of the blockchain
        tx_user_sent = [[tx.amount for tx in block.transactions if tx.sender ==
                         participant] for block in self.blockchain]
        # Fetch a list of all sent coin amounts for the given person (empty lists are returned if the person was NOT the sender)
        # This fetches sent amounts of open transactions (to avoid double spending)
        tx_user_sent_in_open_transactions = [
            tx.amount for tx in self.open_transactions if tx.sender == participant]
        tx_user_sent.append(tx_user_sent_in_open_transactions)
        amount_user_sent = reduce(
            lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_user_sent, 0)

        # This fetches received coin amounts of transactions that were already included in blocks of the blockchain
        # We ignore open transactions here because you shouldn"t be able to spend coins before the transaction was confirmed + included in a block
        tx_user_received = [[tx.amount for tx in block.transactions if tx.recipient ==
                             participant] for block in self.blockchain]
        amount_user_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(
            tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_user_received, 0)

        # Returns the available funds a user has
        return amount_user_received - amount_user_sent

    def add_txn(self, sender, recipient, signature, amount=1.00, is_receiving=False):
        transaction = Transaction(sender, recipient, amount, signature)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            self.save_data()
            if not is_receiving:
                for node in self.peer_nodes:
                    url = f"http://{node}/broadcast-transaction"
                    try:
                        response = requests.post(url, json={
                                                 "sender": sender, "recipient": recipient, "amount": amount, "signature": signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print("Transaction declined!!! needs resolving.")
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        return False

    def mine_block(self):
        if self.public_key is None:
            return None
        else:
            last_block = self.blockchain[-1]
            hashed_block = hash_block(last_block)
            proof = self.proof_of_work()
            print(proof)

            reward_transaction = Transaction(
                "Mining", self.public_key, self.MINING_REWARD, "")

            copied_open_txns = self.open_transactions[:]

            for tx in copied_open_txns:
                if not Wallet.verify_transaction(tx):
                    return None

            copied_open_txns.append(reward_transaction)

            new_block = Block(len(self.blockchain), hashed_block,
                              copied_open_txns, proof, time())

            self.blockchain.append(new_block)
            self.open_transactions = []
            self.save_data()

            for node in self.peer_nodes:
                url = f"http://{node}/broadcast-block"
                converted_block = new_block.__dict__.copy()
                converted_block["transactions"] = [
                    tx.__dict__ for tx in converted_block["transactions"]]
                try:
                    response = requests.post(
                        url, json={"block": converted_block})
                    if response.status_code == 400 or response.status_code == 500:
                        print("Block declined, needs resolving.")
                    if response.status_code == 409:
                        self.resolve_conflicts = True
                except requests.exceptions.ConnectionError:
                    continue

            return new_block

    def add_peer_node(self, node):
        self.peer_nodes.add(node)

    def get_peer_nodes(self):
        return self.peer_nodes

    def remove_peer_node(self, node):
        self.peer_nodes.discard(node)

    def add_broadcasted_block(self, block):
        transactions = [Transaction(
            tx["sender"], tx["recipient"], tx["signature"], tx["amount"]) for tx in block["transactions"]]
        proof_is_valid = Verification.valid_proof(
            transactions[:-1], block["previous_hash"], block["proof"])
        hashes_match = hash_block(
            self.blockchain[-1]) == block["previous_hash"]
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(
            block["index"], block["previous_hash"], transactions, block["proof"], block["timestamp"])
        self.blockchain.append(converted_block)
        stored_transactions = self.open_transactions[:]
        for itx in block["transactions"]:
            for opentx in stored_transactions:
                if opentx.sender == itx["sender"] and opentx.recipient == itx["recipient"] and opentx.amount == itx["amount"] and opentx.signature == itx["signature"]:
                    try:
                        self.open_transactions.remove(opentx)
                    except ValueError:
                        print("Item was already removed.")
        self.save_data()
        return True

    def resolve_chain_conflict(self):
        winner_chain = self.blockchain
        replace = False
        for node in self.peer_nodes:
            url = "http://{}/blockchain".format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [Block(block["index"], block["previous_hash"], [Transaction(
                    tx["sender"], tx["recipient"], tx["signature"], tx["amount"]) for tx in block["transactions"]],
                    block["proof"], block["timestamp"]) for block in node_chain]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        self.blockchain = winner_chain
        if replace:
            self.open_transactions = []
        self.save_data()
        return replace
