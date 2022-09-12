from flask import Flask, jsonify, request
from flask_cors import CORS

from blockchain import Blockchain
from wallet import Wallet
from utility.verification import Verification


app = Flask(__name__)

CORS(app)


@app.route("/create-node/<uid>", methods=["POST"])
def create_blockchain_and_wallet(uid):
    global wallet
    global blockchain
    wallet = Wallet(uid)
    wallet.create_keys()
    if wallet.save_keys():
        blockchain = Blockchain(wallet.public_key, uid)
        blockchain.save_data()

        # chain = blockchain.blockchain
        # dict_chain = [block.__dict__.copy() for block in chain]
        # for dict_block in dict_chain:
        #     dict_block["transactions"] = [
        #         tx.__dict__ for tx in dict_block["transactions"]]

        # open_txns = blockchain.open_transactions
        # dict_txns = [tx.to_ordered_dict() for tx in open_txns]

        response = {
            # "blockchain": dict_chain,
            # "message": "Blockchain fetched successfully.",
            # "wallet": {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "balance": blockchain.get_balance(wallet.public_key),
            "wallet_set_up": wallet.public_key is not None,
            # },
            # "open_transactions": dict_txns,
            # "all_available_peer_nodes": list(blockchain.get_peer_nodes())
        }
        return jsonify(response), 200
    else:
        response = {
            "wallet_public_key": wallet.public_key,
            "wallet_set_up": wallet.public_key is not None,
            "message": "Wallet creation failed."
        }
        return jsonify(response), 500


@app.route("/load-node/<uid>", methods=["GET"])
def load_blockchain_and_wallet(uid):
    global wallet
    global blockchain
    wallet = Wallet(uid)
    if wallet.load_keys():
        blockchain = Blockchain(wallet.public_key, uid)

        # chain = blockchain.blockchain
        # dict_chain = [block.__dict__.copy() for block in chain]
        # for dict_block in dict_chain:
        #     dict_block["transactions"] = [
        #         tx.__dict__ for tx in dict_block["transactions"]]

        # open_txns = blockchain.open_transactions
        # dict_txns = [tx.to_ordered_dict() for tx in open_txns]

        response = {
            # "blockchain": dict_chain,
            # "message": "Blockchain fetched successfully.",
            # "wallet": {
            "public_key": wallet.public_key,
            "private_key": wallet.private_key,
            "balance": blockchain.get_balance(wallet.public_key),
            "wallet_set_up": wallet.public_key is not None,
            # },
            # "open_transactions": dict_txns,
            # "all_available_peer_nodes": list(blockchain.get_peer_nodes())
        }
        return jsonify(response), 200
    else:
        response = {
            "wallet_public_key": wallet.public_key,
            "wallet_set_up": wallet.public_key is not None,
            "message": "Wallet load failed."
        }
        return jsonify(response), 500


@app.route("/blockchain/<uid>", methods=["GET"])
def get_blockchain(uid):
    #  New for frontend
    global wallet
    global blockchain
    wallet = Wallet(uid)
    if wallet.load_keys():
        blockchain = Blockchain(wallet.public_key, uid)

        chain = blockchain.blockchain
        dict_chain = [block.__dict__.copy() for block in chain]
        for dict_block in dict_chain:
            dict_block["transactions"] = [
                tx.__dict__ for tx in dict_block["transactions"]]

        open_txns = blockchain.open_transactions
        dict_txns = [tx.to_ordered_dict() for tx in open_txns]

        response = {
            "blockchain": dict_chain,
            "message": "Blockchain fetched successfully.",
            "wallet": {
                "public_key": wallet.public_key,
                "private_key": wallet.private_key,
                "balance": blockchain.get_balance(wallet.public_key),
                "wallet_set_up": wallet.public_key is not None,
            },
            "open_transactions": dict_txns,
            "all_available_peer_nodes": list(blockchain.get_peer_nodes())
        }
        return jsonify(response), 200
    else:
        response = {
            "wallet_public_key": wallet.public_key,
            "wallet_set_up": wallet.public_key is not None,
            "message": "Wallet load failed."
        }
        return jsonify(response), 500
    # Old code
    # chain = blockchain.blockchain
    # dict_chain = [block.__dict__.copy() for block in chain]
    # for dict_block in dict_chain:
    #     dict_block["transactions"] = [
    #         tx.__dict__ for tx in dict_block["transactions"]]
    # response = {
    #     "blockchain": dict_chain,
    #     "message": "Blockchain fetched successfully."
    # }
    # return jsonify(response), 200


@app.route("/transactions", methods=["GET"])
def get_open_transactions():
    open_txns = blockchain.open_transactions
    dict_txns = [tx.to_ordered_dict() for tx in open_txns]
    response = {
        "open_transactions": dict_txns,
        "message": "Open transactions fetched successfully."
    }
    return jsonify(response), 200


@app.route("/wallet", methods=["GET"])
def get_wallet():
    if wallet.load_keys():
        if wallet.public_key is not None:
            response = {
                "wallet_public_key": wallet.public_key,
                "wallet_set_up": wallet.public_key is not None,
                "message": "Wallet fetched successfully."
            }

            return jsonify(response), 200
        else:
            response = {
                "wallet_public_key": wallet.public_key,
                "wallet_set_up": wallet.public_key is not None,
                "message": "Wallet fetch failed. Wallet not set up."
            }
            return jsonify(response), 500
    else:
        response = {
            "wallet_public_key": wallet.public_key,
            "message": "Wallet load failed.",
            "wallet_set_up": wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route("/balance/<user_public_key>", methods=["GET"])
def get_balance(user_public_key):
    # accepting this user_public_key for frontend to fetch balance for every user.
    if user_public_key == "" or user_public_key is None:
        response = {
            "message": "Please attach user public key.",
            "wallet_set_up": wallet.public_key is not None
        }
        return jsonify(response), 400

    if wallet.public_key is not None:
        user_balance = blockchain.get_balance(user_public_key)
        if user_balance is not None:
            response = {
                "user_balance": user_balance,
                "message": "User balance fetched successfully.",
                "wallet_set_up": wallet.public_key is not None
            }
            return jsonify(response), 200
    else:
        response = {
            "user_balance": None,
            "message": "Balance fetch failed. Wallet not set up.",
            "wallet_set_up": wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route("/nodes", methods=["GET"])
def get_all_nodes():
    response = {
        "message": "Nodes fetched successfully.",
        "all_available_peer_nodes": list(blockchain.get_peer_nodes())
    }
    return jsonify(response), 200


@app.route("/wallet", methods=["POST"])
def create_wallet():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            "wallet_public_key": wallet.public_key,
            "wallet_set_up": wallet.public_key is not None,
            "message": "Wallet created successfully."
        }
        return jsonify(response), 201
    else:
        response = {
            "wallet_public_key": wallet.public_key,
            "wallet_set_up": wallet.public_key is not None,
            "message": "Wallet creation failed."
        }
        return jsonify(response), 500


@app.route("/transaction", methods=["POST"])
def create_transaction():
    # Moved in end for frontend
    # if wallet.public_key is None:
    #     response = {
    #         "wallet_set_up": wallet.public_key is not None,
    #         "balance": None,
    #         "transaction": None,
    #         "message": "Wallet is not setup."
    #     }
    #     return jsonify(response), 400
    values = request.get_json()
    if not values:
        response = {
            "wallet": {
                "public_key": None,
                "private_key": None,
                "wallet_set_up":  None,
                "balance": None,
                "transaction": None,
                "message": "Attach valid data in body."
            },
            "open_transactions": None,
            "message": "Attach valid data in body."
        }
        return jsonify(response), 400
    required_fields = ["sender", "recipient", "amount", "uid"]
    if not all(field in values for field in required_fields):
        response = {
            "wallet": {
                "wallet_set_up": None,
                "public_key": None,
                "private_key": None,
                "balance": None,
                "transaction": None,
                "message": "Required field is missing in body."
            },
            "open_transactions": None,
            "message": "Required field is missing in body."
        }
        return jsonify(response), 400
    uid = values["uid"]
    sender = values["sender"]
    recipient = values["recipient"]
    amount = values["amount"]
    global wallet
    global blockchain
    wallet = Wallet(uid)
    if wallet.load_keys():
        blockchain = Blockchain(wallet.public_key, uid)
        signature = wallet.sign_transaction(sender, recipient, float(amount))
        success = blockchain.add_txn(
            sender, recipient, signature, float(amount))
        open_txns = blockchain.open_transactions
        dict_txns = [tx.to_ordered_dict() for tx in open_txns]
        balance = blockchain.get_balance(sender)
        if success:
            response = {
                "wallet": {
                    "wallet_set_up": wallet.public_key is not None,
                    "balance": balance,
                    "message": "Transaction success.",
                    "public_key": wallet.public_key,
                    "private_key": wallet.private_key,
                },
                "open_transactions": dict_txns,
                "message": "Open transaction created successfully.",
            }
            return jsonify(response), 201
        else:
            message = "Transaction failed." + \
                "Insufficient balance." if balance < float(
                    amount) else "Verification failed."
            response = {
                "wallet": {
                    "wallet_set_up": wallet.public_key is not None,
                    "public_key": wallet.public_key,
                    "private_key": wallet.private_key,
                    "balance": balance,
                    "transaction": None,
                    "message": message
                },
                "open_transactions": dict_txns,
                "message": message,
            }
            return jsonify(response), 400
    else:
        response = {
            "wallet": {
                "wallet_set_up": wallet.public_key is not None,
                "balance": None,
                "transaction": None,
                "public_key": wallet.public_key,
                "private_key": wallet.private_key,
            },
            "open_transactions": dict_txns,
            "message": "Wallet load failed."
        }
        return jsonify(response), 500


@app.route("/mine/<uid>", methods=["POST"])
def mine(uid):
    global wallet
    global blockchain
    wallet = Wallet(uid)
    if wallet.load_keys():
        blockchain = Blockchain(wallet.public_key, uid)
        block = blockchain.mine_block()
        # blockchain.save_data() //commented because already saving it inside mine_block() function.
        # Commented for frontend
        # open_transactions_length = len(blockchain.open_transactions)
        # if open_transactions_length == 0:
        #     response = {
        #         "mined_block": None,
        #         "open_transactions": blockchain.open_transactions,
        #         "wallet_set_up": wallet.public_key is not None,
        #         "message": "No open transaction available to mine.",
        #     }
        #     return jsonify(response), 200
        if block is not None:
            chain = blockchain.blockchain
            dict_chain = [block.__dict__.copy() for block in chain]
            for dict_block in dict_chain:
                dict_block["transactions"] = [
                    tx.__dict__ for tx in dict_block["transactions"]]

            open_txns = blockchain.open_transactions
            dict_txns = [tx.to_ordered_dict() for tx in open_txns]

            dict_block = block.__dict__.copy()
            dict_block["transactions"] = [
                tx.__dict__ for tx in dict_block["transactions"]]
            response = {
                "mined_block": dict_block,
                "blockchain": dict_chain,
                "open_transactions": dict_txns,
                "wallet": {
                    "public_key": wallet.public_key,
                    "private_key": wallet.private_key,
                    "balance": blockchain.get_balance(wallet.public_key),
                    "wallet_set_up": wallet.public_key is not None,
                },
                "message": "Block mined successfully.",
            }
            return jsonify(response), 201
        else:
            response = {
                "mined_block": None,
                "open_transactions": blockchain.open_transactions,
                "message": "Block mining failed.",
            }
            return jsonify(response), 500
    else:
        response = {
            "wallet_public_key": wallet.public_key,
            "wallet_set_up": wallet.public_key is not None,
            "message": "Wallet load failed."
        }
        return jsonify(response), 500


@app.route("/node",  methods=["POST"])
def add_node():
    values = request.get_json()
    if not values:
        response = {
            "message": "Please add valid data in body."
        }
        return jsonify(response), 400
    if "node" and "uid" not in values:
        response = {
            "message": "Please add node/ 'or' /uid key with valid data in body."
        }
        return jsonify(response), 400
    global wallet
    global blockchain
    uid = values["uid"]
    node = values["node"]
    wallet = Wallet(uid)
    if wallet.load_keys():
        blockchain = Blockchain(wallet.public_key, uid)
        blockchain.add_peer_node(node)
        blockchain.save_data()
        response = {
            "message": "Peer node added successfully.",
            "all_available_peer_nodes": list(blockchain.get_peer_nodes())
        }
        return jsonify(response), 201
    else:
        response = {
            "wallet_public_key": wallet.public_key,
            "wallet_set_up": wallet.public_key is not None,
            "message": "Wallet load failed."
        }
        return jsonify(response), 500


@app.route("/broadcast-transaction", methods=["POST"])
def broadcast_transaction():
    values = request.get_json()
    if not values:
        response = {
            "message": "Please add valid data in body.",
            "transaction": None
        }
        return jsonify(response), 400
    required = ["sender", "recipient", "amount", "signature"]
    if not all(key in values for key in required):
        response = {
            "message": "Some data is missing in body.",
            "transaction": None
        }
        return jsonify(response), 400
    success = blockchain.add_txn(
        values["recipient"],
        values["sender"],
        values["signature"],
        values["amount"],
        is_receiving=True
    )
    if success:
        response = {
            "message": "Transaction added successfully.",
            "transaction": {
                "sender": values["sender"],
                "recipient": values["recipient"],
                "amount": values["amount"],
                "signature": values["signature"]
            }
        }
        return jsonify(response), 201
    else:
        response = {
            "message": "Transaction creation failed.",
            "transaction": None
        }
        return jsonify(response), 500


@app.route("/broadcast-block", methods=["POST"])
def broadcast_block():
    values = request.get_json()
    if not values:
        response = {"message": "Please add valid data in body."}
        return jsonify(response), 400
    if "block" not in values:
        response = {"message": "Block data is missing in body."}
        return jsonify(response), 400
    block = values["block"]
    if block["index"] == blockchain.blockchain[-1].index + 1:
        if blockchain.add_broadcasted_block(block):
            response = {"message": "Block added successfully."}
            return jsonify(response), 201
        else:
            response = {"message": "Block seems to be invalid."}
            return jsonify(response), 409
    elif block["index"] > blockchain.blockchain[-1].index:
        response = {
            "message": "Blockchain seems to differ from local blockchain."}
        blockchain.resolve_conflicts = True
        return jsonify(response), 200
    else:
        response = {
            "message": "Blockchain seems to be shorter, block not added."}
        return jsonify(response), 409


@app.route("/resolve-conflicts", methods=["POST"])
def resolve_conflicts():
    replaced = blockchain.resolve_chain_conflict()
    if replaced:
        response = {"message": "Chain was replaced!"}
    else:
        response = {"message": "Local chain kept!"}
    return jsonify(response), 200


@app.route("/node", methods=["DELETE"])
def delete_node():
    # Added for frontend
    values = request.get_json()
    if not values:
        response = {
            "message": "Please add valid data in body."
        }
        return jsonify(response), 400
    if "node" and "uid" not in values:
        response = {
            "message": "Please add node/ 'or' /uid key with valid data in body."
        }
        return jsonify(response), 400
    global wallet
    global blockchain
    uid = values["uid"]
    node = values["node"]
    wallet = Wallet(uid)
    if wallet.load_keys():
        blockchain = Blockchain(wallet.public_key, uid)
        blockchain.remove_peer_node(node)
        blockchain.save_data()
        response = {
            "message": "Peer node deleted successfully.",
            "all_available_peer_nodes": list(blockchain.get_peer_nodes())
        }
        return jsonify(response), 200
    else:
        response = {
            "wallet_public_key": wallet.public_key,
            "wallet_set_up": wallet.public_key is not None,
            "message": "Wallet load failed."
        }
        return jsonify(response), 500

    # Commented for frontend
    # if node_name == "" or node_name is None:
    #     response = {
    #         "message": "Please attach a node in param to delete.",
    #         "all_available_peer_nodes": list(blockchain.get_peer_nodes())
    #     }
    #     return jsonify(response), 400
    # blockchain.remove_peer_node(node_name)
    # response = {
    #     "message": "Peer node deleted successfully.",
    #     "all_available_peer_nodes": list(blockchain.get_peer_nodes())
    # }
    # return jsonify(response), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
