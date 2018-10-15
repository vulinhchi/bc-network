import requests


class Blockchain:
    def __init__(self):
        self.current_transaction = []
        self.chain = []
        self.nodes = set()

        self.new_block(previous_hash = '1', proof = 100)


