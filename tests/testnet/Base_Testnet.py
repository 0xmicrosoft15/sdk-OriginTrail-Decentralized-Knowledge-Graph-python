import json
import time
import pytest
import random
import os
import traceback
import sys
from uuid import uuid4
from dotenv import load_dotenv

from dkg import DKG
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.constants import BlockchainIds
from web3.exceptions import ContractCustomError

# Load .env values
load_dotenv()

# Blockchain config
BLOCKCHAIN = BlockchainIds.BASE_TESTNET.value
PRIVATE_KEY = os.getenv("TESTNET_PRIVATE_KEY")
PUBLIC_KEY = os.getenv("TESTNET_PUBLIC_KEY")

assert PRIVATE_KEY, "TESTNET_PRIVATE_KEY is missing in .env"
assert PUBLIC_KEY, "TESTNET_PUBLIC_KEY is missing in .env"

# Set env variable for BlockchainProvider to pick up
os.environ["PRIVATE_KEY"] = PRIVATE_KEY

# Constants
OT_NODE_PORT = 8900
SHOW_FULL_TRACEBACK = False

# Fixed nodes
nodes = [
    {"name": "Node 01", "hostname": "https://v6-pegasus-node-01.origin-trail.network"},
    {"name": "Node 08", "hostname": "https://v6-pegasus-node-08.origin-trail.network"},
    {"name": "Node 09", "hostname": "https://v6-pegasus-node-09.origin-trail.network"},
]

# Helpers
words = ['Galaxy', 'Nebula', 'Orbit', 'Quantum', 'Pixel', 'Velocity', 'Echo', 'Nova']
descriptions = [
    'This asset explores the mysteries of {}.',
    'An in-depth look into {} technologies.',
    'Unlocking the power of {} in modern systems.',
    'How {} shapes our digital future.',
    'A fresh perspective on {} innovation.',
]

def print_exception(e, node_name="Unknown"):
    print(f"\n❌ Error on {node_name}")
    print(f"🔺 Type: {type(e).__name__}")
    print(f"🧵 Message: {str(e)}")
    tb = traceback.extract_tb(sys.exc_info()[2])
    user_tb = [entry for entry in tb if "site-packages" not in entry.filename]
    if user_tb:
        last = user_tb[-1]
        print(f"📍 Location: {last.filename}, line {last.lineno}, in {last.name}")
    else:
        print("📍 Location: (inside dependency)")
    if SHOW_FULL_TRACEBACK:
        print("🧱 Full Traceback:")
        traceback.print_exc()

@pytest.mark.parametrize("node_index", range(len(nodes)))
@pytest.mark.flaky(reruns=0, reruns_delay=5)
def test_asset_lifecycle(node_index):
    node = nodes[node_index]
    try:
        node_provider = NodeHTTPProvider(
            endpoint_uri=f"{node['hostname']}:{OT_NODE_PORT}",
            api_version="v1",
        )
        blockchain_provider = BlockchainProvider(BLOCKCHAIN)

        config = {
            "max_number_of_retries": 300,
            "frequency": 2,
        }
        dkg = DKG(node_provider, blockchain_provider, config)

        print(f"\n======================== NODE INFO for {node['name']}")

        word = random.choice(words)
        template = random.choice(descriptions)
        content = {
            "public": {
                "@context": "https://schema.org",
                "@id": f"urn:ka:{node['name'].replace(' ', '').lower()}-{uuid4()}",
                "@type": "CreativeWork",
                "name": f"DKG {word} {int(time.time())}",
                "description": template.format(word),
            }
        }

        # Create Asset
        start = time.perf_counter()
        create_asset_result = dkg.asset.create(
            content=content,
            options={
                "epochs_num": 2,
                "minimum_number_of_finalization_confirmations": 3,
                "minimum_number_of_node_replications": 3,
            },
        )
        print(f"ASSET CREATED on {node['name']} in {time.perf_counter() - start:.2f}s")
        ual = create_asset_result.get("UAL")
        assert ual, f"UAL missing after publish on {node['name']}"
        print(f"✅Successfully published asset on {node['name']}")

        # Query
        start = time.perf_counter()
        query_result = dkg.graph.query(
            """
            PREFIX schema: <http://schema.org/>
            SELECT ?s ?name ?description
            WHERE {
                ?s schema:name ?name ;
                   schema:description ?description .
            }
            """
        )
        print(f"QUERY in {time.perf_counter() - start:.2f}s")
        assert query_result, f"Query returned no results on {node['name']}"
        print(f"✅Successfully queried graph on {node['name']}")

        # Get on same node
        start = time.perf_counter()
        get_result = dkg.asset.get(ual)
        print(f"GET in {time.perf_counter() - start:.2f}s")
        assert get_result.get("assertion"), f"Get returned no assertion on {node['name']}"
        print(f"✅Successfully got asset on {node['name']}")

        # Get on different random node (sync)
        other_indexes = [i for i in range(len(nodes)) if i != node_index]
        other_index = random.choice(other_indexes)
        other_node = nodes[other_index]

        other_provider = NodeHTTPProvider(
            endpoint_uri=f"{other_node['hostname']}:{OT_NODE_PORT}",
            api_version="v1",
        )
        other_dkg = DKG(other_provider, blockchain_provider, config)

        start = time.perf_counter()
        other_get = other_dkg.asset.get(ual)
        print(f"GET from {other_node['name']} in {time.perf_counter() - start:.2f}s")
        assert other_get.get("assertion"), f"Get failed from {other_node['name']}"
        print(f"✅Successfully Synced asset on {other_node['name']}")

        # Finality
        start = time.perf_counter()
        finality_result = dkg.graph.publish_finality(ual)
        print(f"FINALITY in {time.perf_counter() - start:.2f}s")
        assert finality_result.get("status") == "FINALIZED", f"Finality not FINALIZED on {node['name']}"
        print(f"✅Finality status is FINALIZED on {node['name']}")

    except Exception as e:
        print_exception(e, node["name"])
        pytest.fail(str(e), pytrace=False)