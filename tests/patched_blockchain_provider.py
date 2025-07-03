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

# Gas price oracles for mainnet networks
GAS_PRICE_ORACLES = {
    'base:8453': "https://api.basescan.org/api?module=gastracker&action=gasoracle",
    'gnosis:100': "https://api.gnosisscan.io/api?module=gastracker&action=gasoracle", 
    'otp:2043': "https://api.origintrail.io/api?module=gastracker&action=gasoracle",
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
            
            # Add gas price oracle for mainnet networks
            if blockchain_id in GAS_PRICE_ORACLES:
                d[path[-1]]["gas_price_oracle"] = GAS_PRICE_ORACLES[blockchain_id]
                
        super().__init__(blockchain_id)
        self.environment = path[0] if config else None
        self.name = blockchain_id
    
    def _get_network_gas_price(self):
        """Override the gas price method with enhanced logic"""
        if self.environment == "development":
            return None

        def fetch_gas_price(oracle_url: str):
            try:
                import requests
                response = requests.get(oracle_url)
                response.raise_for_status()
                data: dict = response.json()

                gas_price = None
                if "fast" in data:
                    gas_price = self.w3.to_wei(data["fast"], "gwei")
                elif "result" in data:
                    gas_price = int(data["result"], 16)
                else:
                    return None
                
                # Ensure minimum gas price (2 gwei = 2,000,000,000 wei)
                min_gas_price = self.w3.to_wei(2, "gwei")
                if gas_price < min_gas_price:
                    return min_gas_price
                
                return gas_price
            except Exception:
                return None

        oracles = self.gas_price_oracle
        if oracles is not None:
            if isinstance(oracles, str):
                oracles = [oracles]

            for oracle_url in oracles:
                gas_price = fetch_gas_price(oracle_url)
                if gas_price is not None:
                    return gas_price

        # Fallback: use network gas price with minimum
        try:
            network_gas_price = self.w3.eth.gas_price
            min_gas_price = self.w3.to_wei(2, "gwei")
            if network_gas_price < min_gas_price:
                return min_gas_price
            return network_gas_price
        except Exception:
            # Final fallback: return minimum gas price
            return self.w3.to_wei(2, "gwei")