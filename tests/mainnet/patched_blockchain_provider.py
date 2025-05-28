from dkg.providers import BlockchainProvider as OriginalBlockchainProvider
from dkg.constants import BLOCKCHAINS
from web3 import Web3

class BlockchainProvider(OriginalBlockchainProvider):
    def __init__(self, blockchain_id):
        # Monkey-patch the global BLOCKCHAINS config before parent class uses it
        BLOCKCHAINS["mainnet"]["base:8453"]["rpc"] = "https://site1.moralis-nodes.com/base/2cb0d661c0614680b84a5c1c91f4d6aa"

        super().__init__(blockchain_id)

        self.environment = "mainnet"
        self.name = blockchain_id