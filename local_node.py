from blockchain import Blockchain
from wallet import Wallet
from utility.verification import Verification

wallet = Wallet()
blockchain = Blockchain(wallet.public_key)

while True:
    print("-" * 20)
    print("Please choose any one")
    print("1 : Send Coins")
    print("2 : Mine Coins")
    print("3 : Create wallet")
    print("4 : Load wallet")
    print("5 : Show user balance")
    print("6 : Validate Blockchain")
    print("o : Show open transaction")
    print("s : Show Blockchain")
    print("q : Quit")
    print("-" * 20)

    user_input = input("Your selection: ")

    if user_input == "1":
        print("-" * 20)
        recipient = input("Enter recipient: ")
        amount = float(input("Enter amount: "))
        if blockchain.add_txn(blockchain.public_key, recipient, "", amount):
            print("-" * 20)
            print("Coins sent.")
            print("-" * 20)
        else:
            print("Insufficient funds!")
    elif user_input == "2":
        print("-" * 20)
        if blockchain.mine_block() is not None:
            print("-" * 20)
            print("Coins mined! You've been rewarded 10.00 coins.")
        print("-" * 20)
    elif user_input == "3":
        wallet.create_keys()
        if wallet.save_keys():
            blockchain = Blockchain(wallet.public_key)
        else:
            print("-" * 20)
            print("Creating wallet failed!!!")
            print("-" * 20)
    elif user_input == "4":
        if wallet.load_keys():
            blockchain = Blockchain(wallet.public_key)
        else:
            print("-" * 20)
            print("Loading wallet failed!!!")
            print("-" * 20)
    elif user_input == "5":
        user = blockchain.public_key
        if user is None:
            print("-" * 20)
            print("Wallet not setup. Unable to fetch balance.")
            print("-" * 20)
        else:
            user_balance = blockchain.get_balance(user)
            print("-" * 20)
            print(f"User balance --> {user} : {user_balance}")
            print("-" * 20)

    elif user_input == "6":
        print("-" * 20)
        if not Verification.verify_blockchain(blockchain.blockchain):
            print("Blockchain Invalid.")
        else:
            print("Blockchain is valid.")
        print("-" * 20)
    elif user_input == "o" or user_input == "O":
        print("-" * 20)
        print(blockchain.open_transactions)
        print("-" * 20)
    elif user_input == "s" or user_input == "S":
        print("-" * 20)
        print(blockchain.blockchain)
        print("-" * 20)
    elif user_input == "q" or user_input == "Q":
        print("-" * 20)
        print("User left!")
        print("-" * 20)
        break
