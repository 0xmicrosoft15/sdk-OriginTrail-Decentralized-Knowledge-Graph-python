from dkg.providers import BlockchainProvider as OriginalBlockchainProvider
from dkg.constants import BLOCKCHAINS
from web3 import Web3

class BlockchainProvider(OriginalBlockchainProvider):
    def __init__(self, blockchain_id):
        # Monkey-patch the global BLOCKCHAINS config before parent class uses it
        BLOCKCHAINS["mainnet"]["base:8453"]["rpc"] = "https://api-base-mainnet-archive.dwellir.com/c5568240-7482-4fe0-8bf9-33c2a7a8ffdc"

        super().__init__(blockchain_id)

        self.environment = "mainnet"
        self.name = blockchain_id