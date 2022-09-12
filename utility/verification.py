from utility.utils import hash_string_256, hash_block
from wallet import Wallet


class Verification:

    @staticmethod
    def validate_proof(transactions, last_hash, proof):
        guess = (str(transactions) + str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        print(guess_hash)
        return guess_hash[0:2] == "ff"

    @classmethod
    def verify_blockchain(cls, blockchain):
        for (index, block) in enumerate(blockchain):
            print(block)
            if index == 0:
                continue
            elif block.previous_hash != hash_block(blockchain[index-1]):
                print("Invalid hashes.")
                return False
            # not including mined block in next check : block.transactions[:-1]
            elif not cls.validate_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print("Invalid Proof of Work.")
                return False
        return True

    @staticmethod
    def verify_transaction(transaction, get_balance, check_balance=True):
        if check_balance:
            user_balance = get_balance(transaction.sender)
            return user_balance >= float(transaction.amount) and Wallet.verify_transaction(transaction)
        return Wallet.verify_transaction(transaction)
