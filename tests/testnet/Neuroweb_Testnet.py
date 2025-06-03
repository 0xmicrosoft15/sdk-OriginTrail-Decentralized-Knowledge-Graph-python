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

# Load environment variables
load_dotenv()

BLOCKCHAIN = BlockchainIds.NEUROWEB_TESTNET.value
PRIVATE_KEY = os.getenv("TESTNET_PRIVATE_KEY")
PUBLIC_KEY = os.getenv("TESTNET_PUBLIC_KEY")

assert PRIVATE_KEY, "TESTNET_PRIVATE_KEY is missing"
assert PUBLIC_KEY, "TESTNET_PUBLIC_KEY is missing"

os.environ["PRIVATE_KEY"] = PRIVATE_KEY

OT_NODE_PORT = 8900

nodes = [
    {"name": "Node 01", "hostname": "https://v6-pegasus-node-01.origin-trail.network"},
    {"name": "Node 08", "hostname": "https://v6-pegasus-node-08.origin-trail.network"},
    {"name": "Node 09", "hostname": "https://v6-pegasus-node-09.origin-trail.network"},
]

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

@pytest.mark.parametrize("node_index", range(len(nodes)))
def test_asset_lifecycle(node_index):
    node = nodes[node_index]
    passed = 0
    failed = 0
    failed_assets = []

    for i in range(15):
        print(f"\n📡 Publishing KA #{i + 1} on {node['name']}")
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

        ual = None
        try:
            node_provider = NodeHTTPProvider(f"{node['hostname']}:{OT_NODE_PORT}", "v1")
            blockchain_provider = BlockchainProvider(BLOCKCHAIN)
            config = {"max_number_of_retries": 300, "frequency": 2}
            dkg = DKG(node_provider, blockchain_provider, config)

            result = dkg.asset.create(content, {
                "epochs_num": 2,
                "minimum_number_of_finalization_confirmations": 3,
                "minimum_number_of_node_replications": 3,
            })

            ual = result.get("UAL")
            assert ual, "UAL not found after publish"
            print(f"✅ Published KA #{i + 1} with UAL: {ual}")

            query_result = dkg.graph.query("""
                PREFIX schema: <http://schema.org/>
                SELECT ?s ?name ?description
                WHERE {
                    ?s schema:name ?name ; schema:description ?description .
                }
            """)
            assert query_result, "Query returned no results"
            print("✅ Query succeeded")

            get_result = dkg.asset.get(ual)
            assert get_result.get("assertion"), "Get failed"
            print("✅ Local get succeeded")

            others = [i for i in range(len(nodes)) if i != node_index]
            other_node = nodes[random.choice(others)]
            other_provider = NodeHTTPProvider(f"{other_node['hostname']}:{OT_NODE_PORT}", "v1")
            other_dkg = DKG(other_provider, blockchain_provider, config)

            remote_get = other_dkg.asset.get(ual)
            assert remote_get.get("assertion"), "Remote get failed"
            print(f"✅ Remote get succeeded on {other_node['name']}")

            passed += 1

        except Exception as e:
            print_exception(e, node['name'])
            reason = (
                "Publish failed — No UAL" if not ual else
                f"Query failed — UAL: {ual}" if "Query returned no results" in str(e) else
                f"Local get failed — UAL: {ual}" if "Get failed" in str(e) else
                f"Remote get failed — UAL: {ual}" if "Remote get failed" in str(e) else
                f"Failed after publish — UAL: {ual}"
            )
            failed_assets.append(f"KA #{i + 1} ({reason})")
            failed += 1
            continue

    print(f"\n──────────── Summary for {node['name']} ────────────")
    print(f"✅ Success: {passed} / 15")
    print(f"❌ Failed: {failed}")
    if failed_assets:
        print("🔍 Failed Assets:")
        for asset in failed_assets:
            print(f"  - {asset}")