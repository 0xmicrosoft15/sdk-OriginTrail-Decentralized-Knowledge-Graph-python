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
    {"name": "Node 04", "hostname": "https://v6-pegasus-node-04.origin-trail.network"},
    {"name": "Node 08", "hostname": "https://v6-pegasus-node-08.origin-trail.network"},
]

words = ['Galaxy', 'Nebula', 'Orbit', 'Quantum', 'Pixel', 'Velocity', 'Echo', 'Nova']
descriptions = [
    'This asset explores the mysteries of {}.',
    'An in-depth look into {} technologies.',
    'Unlocking the power of {} in modern systems.',
    'How {} shapes our digital future.',
    'A fresh perspective on {} innovation.',
]

# Global stats tracker
global_stats = {
    BLOCKCHAIN: {}
}

error_stats = {}

def print_exception(e, node_name="Unknown"):
    print(f"\n❌ Error on {node_name}")
    print(f"🔺 Type: {type(e).__name__}")
    print(f"🧵 Message: {str(e)}")
    tb = traceback.extract_tb(sys.exc_info()[2])
    user_tb = [entry for entry in tb if "site-packages" not in entry.filename]
    if user_tb:
        last = user_tb[-1]
        print(f"📍 Location: {last.filename}, line {last.lineno}, in {last.name}")

    # Collect error stats
    msg = str(e).split("\n")[0]
    error_key = f"{type(e).__name__}: {msg}"
    if node_name not in error_stats:
        error_stats[node_name] = {}
    error_stats[node_name][error_key] = error_stats[node_name].get(error_key, 0) + 1

@pytest.mark.parametrize("node_index", range(len(nodes)))
def test_asset_lifecycle(node_index):
    node = nodes[node_index]
    passed = 0
    failed = 0
    failed_assets = []

    for i in range(1):
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
            assert ual, "Publish failed — No UAL"
            print(f"✅ Published KA #{i + 1} with UAL: {ual}")

            query_result = dkg.graph.query("""
                PREFIX schema: <http://schema.org/>
                SELECT ?s ?name ?description
                WHERE {
                    ?s schema:name ?name ; schema:description ?description .
                }
            """)
            assert query_result, f"Query failed — UAL: {ual}"
            print("✅ Query succeeded")

            get_result = dkg.asset.get(ual)
            assert get_result.get("assertion"), f"Local get failed — UAL: {ual}"
            print("✅ Local get succeeded")

            others = [i for i in range(len(nodes)) if i != node_index]
            other_node = nodes[random.choice(others)]
            other_provider = NodeHTTPProvider(f"{other_node['hostname']}:{OT_NODE_PORT}", "v1")
            other_dkg = DKG(other_provider, blockchain_provider, config)

            remote_get = other_dkg.asset.get(ual)
            assert remote_get.get("assertion"), f"Remote get failed — UAL: {ual}"
            print(f"✅ Remote get succeeded on {other_node['name']}")

            passed += 1

        except Exception as e:
            print_exception(e, node['name'])
            msg = str(e)
            if 'UAL' in msg:
                failed_assets.append(f"KA #{i + 1} ({msg})")
            else:
                reason = "Publish failed — No UAL" if not ual else f"Failed after publish — UAL: {ual}"
                failed_assets.append(f"KA #{i + 1} ({reason})")
            failed += 1
            continue

    print(f"\n──────────── Summary for {node['name']} ────────────")
    print(f"✅ Success: {passed} / 1 -> {round(passed / 15 * 100, 2)}%")
    print(f"❌ Failed: {failed}")
    if failed_assets:
        print("🔍 Failed Assets:")
        for asset in failed_assets:
            print(f"  - {asset}")

    # Save to global stats
    global_stats[BLOCKCHAIN][node['name']] = {"success": passed, "failed": failed}

# Hook to print final stats after all tests
def pytest_sessionfinish(session, exitstatus):
    print("\n\n📊 Global Publish Summary:")

    for blockchain, node_data in global_stats.items():
        print(f"\n🔗 Blockchain: {blockchain}")
        total_success = 0
        total_failed = 0
        for node_name, results in node_data.items():
            s, f = results["success"], results["failed"]
            total_success += s
            total_failed += f
            rate = round(s / (s + f) * 100, 2)
            print(f"  • {node_name}: ✅ {s} / ❌ {f} ({rate}%)")

        total = total_success + total_failed
        total_rate = round(total_success / total * 100, 2) if total > 0 else 0
        print(f"  📦 TOTAL: ✅ {total_success} / ❌ {total_failed} -> {total_rate}%")

    print("\n\n📊 Error Breakdown by Node:")
    for node_name, errors in error_stats.items():
        print(f"\n🔧 {node_name}")
        for message, count in errors.items():
            print(f"  • {count}x {message}")
__all__ = ["error_stats", "global_stats"]
