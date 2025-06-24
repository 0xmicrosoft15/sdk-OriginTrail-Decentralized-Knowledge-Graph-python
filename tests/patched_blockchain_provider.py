from dkg.providers import BlockchainProvider as OriginalBlockchainProvider
from dkg.constants import BLOCKCHAINS
import os

# Map blockchain_id to (env_var, blockchains_path)
BLOCKCHAIN_RPC_CONFIG = {
    # Mainnet
    'base:8453':      ("BASE_MAINNET_RPC",    ["mainnet", "base:8453"]),
    'gnosis:100':     ("GNOSIS_MAINNET_RPC",   ["mainnet", "gnosis:100"]),
    'otp:2043':       ("NEUROWEB_MAINNET_RPC", ["mainnet", "otp:2043"]),
    # Testnet
    'base:84532':      ("BASE_TESTNET_RPC",    ["testnet", "base:84532"]),
    'gnosis:10200':    ("GNOSIS_TESTNET_RPC",  ["testnet", "gnosis:10200"]),
    'otp:20430':       ("NEUROWEB_TESTNET_RPC", ["testnet", "otp:20430"]),
}

class BlockchainProvider(OriginalBlockchainProvider):
    def __init__(self, blockchain_id):
        config = BLOCKCHAIN_RPC_CONFIG.get(blockchain_id)
        if config:
            env_var, path = config
            rpc_url = os.getenv(env_var)
            if not rpc_url:
                raise RuntimeError(f"Missing required env var: {env_var}")
            # Patch the global BLOCKCHAINS config
            d = BLOCKCHAINS
            for key in path[:-1]:
                d = d[key]
            d[path[-1]]["rpc"] = rpc_url
        super().__init__(blockchain_id)
        self.environment = path[0] if config else None
        self.name = blockchain_id