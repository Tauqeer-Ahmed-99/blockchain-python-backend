from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Random
import binascii
from hashlib import sha256


class Wallet:
    def __init__(self, uid):
        self.private_key = None
        self.public_key = None
        self.uid = uid

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def generate_keys(self):
        private_key = RSA.generate(1024, Crypto.Random.new().read)
        public_key = private_key.publickey()
        return (
            binascii.hexlify(private_key.exportKey(
                format="DER")).decode("ascii"),
            binascii.hexlify(public_key.exportKey(
                format="DER")).decode("ascii")
        )

    def save_keys(self):
        if self.private_key is not None and self.public_key is not None:
            try:
                with open(f"wallet-{self.uid}.txt", mode="w") as file:
                    file.write(self.public_key)
                    file.write("\n")
                    file.write(self.private_key)
                return True
            except (IOError, IndexError):
                print("Saving wallet failed!!!")
                return False

    def load_keys(self):
        try:
            with open(f"wallet-{self.uid}.txt", mode="r") as file:
                file_content = file.readlines()
                self.public_key = file_content[0][:-1]
                self.private_key = file_content[1]
            return True
        except (IOError, IndexError):
            print("loading wallet failed!!!")
            return False

    def sign_transaction(self, sender, recipient, amount):
        signer = PKCS1_v1_5.new(
            RSA.importKey(
                binascii.unhexlify(self.private_key)
            )
        )
        hashed_transaction = SHA256.new((str(sender) + str(recipient) +
                                         str(amount)).encode('utf8'))
        signature = signer.sign(hashed_transaction)
        return binascii.hexlify(signature).decode("ascii")

    @staticmethod
    def verify_transaction(transaction):
        public_key = RSA.importKey(binascii.unhexlify(transaction.sender))
        verifier = PKCS1_v1_5.new(public_key)
        hashed_transaction = SHA256.new(
            (str(transaction.sender) + str(transaction.recipient) +
             str(transaction.amount)).encode("utf8")
        )
        return verifier.verify(hashed_transaction, binascii.unhexlify(transaction.signature))
