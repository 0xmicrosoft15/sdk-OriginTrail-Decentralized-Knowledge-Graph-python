import json
import time
import pytest
import random
import os
import traceback
import sys
from uuid import uuid4
from dotenv import load_dotenv
import multiprocessing

from dkg import DKG
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.constants import BlockchainIds

from tests.testnet.stats_tracker import global_stats, error_stats

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

global_stats[BLOCKCHAIN] = {}

def print_exception(e, node_name="Unknown"):
    print(f"\n❌ Error on {node_name}")
    print(f"🔺 Type: {type(e).__name__}")
    print(f"🧵 Message: {str(e)}")
    tb = traceback.extract_tb(sys.exc_info()[2])
    user_tb = [entry for entry in tb if "site-packages" not in entry.filename]
    if user_tb:
        last = user_tb[-1]
        print(f"📍 Location: {last.filename}, line {last.lineno}, in {last.name}")
    msg = str(e).split("\n")[0]
    error_key = f"{type(e).__name__}: {msg}"
    if node_name not in error_stats:
        error_stats[node_name] = {}
    error_stats[node_name][error_key] = error_stats[node_name].get(error_key, 0) + 1

def lifecycle_worker(node, node_index, i, result_queue):
    try:
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

        node_provider = NodeHTTPProvider(f"{node['hostname']}:{OT_NODE_PORT}", "v1")
        blockchain_provider = BlockchainProvider(BLOCKCHAIN)
        config = {"max_number_of_retries": 300, "frequency": 2}
        dkg = DKG(node_provider, blockchain_provider, config)

        step = "publish"
        result = dkg.asset.create(content, {
            "epochs_num": 2,
            "minimum_number_of_finalization_confirmations": 3,
            "minimum_number_of_node_replications": 3,
        })
        ual = result.get("UAL")
        if not ual:
            raise Exception("Publish failed — No UAL")
        print(f"✅ Published KA #{i + 1} with UAL: {ual}")

        step = "query"
        query_result = dkg.graph.query("""
            PREFIX schema: <http://schema.org/>
            SELECT ?s ?name ?description
            WHERE {
                ?s schema:name ?name ; schema:description ?description .
            }
        """)
        if not query_result:
            raise Exception("Query failed")

        step = "get"
        get_result = dkg.asset.get(ual)
        if not get_result.get("assertion"):
            raise Exception("Local get failed")

        step = "remote get"
        others = [x for x in range(len(nodes)) if x != node_index]
        other_node = nodes[random.choice(others)]
        other_provider = NodeHTTPProvider(f"{other_node['hostname']}:{OT_NODE_PORT}", "v1")
        other_dkg = DKG(other_provider, blockchain_provider, config)
        remote_get = other_dkg.asset.get(ual)
        if not remote_get.get("assertion"):
            raise Exception("Remote get failed")

        result_queue.put(("success", None))
    except Exception as e:
        result_queue.put(("failure", str(e)))

@pytest.mark.parametrize("node_index", range(len(nodes)))
def test_asset_lifecycle(node_index):
    node = nodes[node_index]
    passed = 0
    failed = 0
    failed_assets = []

    for i in range(10):
        print(f"\n📡 Publishing KA #{i + 1} on {node['name']}")
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=lifecycle_worker, args=(node, node_index, i, result_queue))
        process.start()
        process.join(timeout=180)

        if process.is_alive():
            process.terminate()
            process.join()
            print(f"⏱️ Timeout: KA #{i + 1} on {node['name']} timed out after 2 minutes.")
            failed_assets.append(f"KA #{i + 1} (timeout after 2 min)")
            failed += 1
        else:
            try:
                status, error = result_queue.get_nowait()
                if status == "success":
                    passed += 1
                else:
                    print(f"❌ KA #{i + 1} failed: {error}")
                    failed_assets.append(f"KA #{i + 1} ({error})")
                    failed += 1
            except Exception:
                failed_assets.append(f"KA #{i + 1} (unknown error)")
                failed += 1

    print(f"\n────────── Summary for {node['name']} ──────────")
    print(f"✅ Success: {passed} / 10")
    print(f"❌ Failed: {failed}")
    if failed_assets:
        print("🔍 Failed Assets:")
        for asset in failed_assets:
            print(f"  - {asset}")

    global_stats[BLOCKCHAIN][node['name']] = {"success": passed, "failed": failed}