import json
import time
import pytest
import random
import os
import traceback
import sys
from uuid import uuid4
from dotenv import load_dotenv
from datetime import datetime
import concurrent.futures
from concurrent.futures import TimeoutError

from tests.patched_blockchain_provider import BlockchainProvider
from dkg import DKG
from dkg.providers import NodeHTTPProvider
from dkg.constants import BlockchainIds
from tests.mainnet.stats_tracker import global_stats, error_stats

load_dotenv()

BLOCKCHAIN = BlockchainIds.BASE_MAINNET.value
OT_NODE_PORT = 8900

nodes = [
    {"name": "Node 25", "hostname": "https://v6-pegasus-node-25.origin-trail.network"},
    {"name": "Node 26", "hostname": "https://v6-pegasus-node-26.origin-trail.network"},
    {"name": "Node 27", "hostname": "https://v6-pegasus-node-27.origin-trail.network"},
    {"name": "Node 28", "hostname": "https://v6-pegasus-node-28.origin-trail.network"},
    {"name": "Node 29", "hostname": "https://v6-pegasus-node-29.origin-trail.network"},
    {"name": "Node 30", "hostname": "https://v6-pegasus-node-30.origin-trail.network"},
]

node_keys = {
    name: {
        "publicKey": os.getenv(f"PY_MAINNET_BASE_{name.replace(' ', '').upper()}_PUBLIC_KEY"),
        "privateKey": os.getenv(f"PY_MAINNET_BASE_{name.replace(' ', '').upper()}_PRIVATE_KEY"),
    }
    for name in [n["name"] for n in nodes]
}

words = ['Galaxy', 'Nebula', 'Orbit', 'Quantum', 'Pixel', 'Velocity', 'Echo', 'Nova']
descriptions = [
    'This asset explores the mysteries of {}.',
    'An in-depth look into {} technologies.',
    'Unlocking the power of {} in modern systems.',
    'How {} shapes our digital future.',
    'A fresh perspective on {} innovation.',
]

def run_with_timeout(func, timeout_seconds=180, operation_name="operation"):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func)
        try:
            result = future.result(timeout=timeout_seconds)
            return result
        except concurrent.futures.TimeoutError:
            print(f"⏰ Timeout after 3 minutes during {operation_name}")
            raise TimeoutError(f"{operation_name} timed out after 3 minutes")
        except Exception as e:
            raise

def get_random_content(node_name):
    word = random.choice(words)
    template = random.choice(descriptions)
    return {
        "public": {
            "@context": "https://www.schema.org",
            "@id": f"urn:ka:{node_name.replace(' ', '').lower()}-{uuid4()}",
            "@type": "CreativeWork",
            "name": f"DKG {word} {int(time.time())}",
            "description": template.format(word),
        }
    }

def log_error(error, node_name, step='unknown', remote_node=None):
    print(f"\n❌ Error on {node_name} during {step}")
    print(f"🔺 Type: {type(error).__name__}")
    print(f"🧵 Message: {str(error)}")
    tb = traceback.extract_tb(sys.exc_info()[2])
    user_tb = [entry for entry in tb if "site-packages" not in entry.filename]
    if user_tb:
        last = user_tb[-1]
        print(f"📍 Location: {last.filename}, line {last.lineno}, in {last.name}")

    # Create a cleaner error message for grouping
    if isinstance(error, TimeoutError) or isinstance(error, concurrent.futures.TimeoutError):
        error_message = f"Timeout after 3 minutes during {step}"
    else:
        try:
            if isinstance(error, dict):
                error_message = error.get("errorType") or str(error)
            elif hasattr(error, "args") and isinstance(error.args[0], dict):
                error_message = error.args[0].get("errorType", str(error))
            else:
                error_message = str(error)
        except Exception:
            error_message = str(error)

    error_message = error_message.splitlines()[0][:100]

    # Create a generic key that groups similar errors
    if remote_node:
        key = f"{step} — {type(error).__name__}: {error_message} on {remote_node}"
    else:
        key = f"{step} — {type(error).__name__}: {error_message}"
    
    # Store errors in a temporary file to ensure persistence across test session
    error_file = "test_output/error_stats.json"
    os.makedirs("test_output", exist_ok=True)
    
    # Load existing errors
    if os.path.exists(error_file):
        with open(error_file, 'r') as f:
            try:
                error_data = json.load(f)
            except:
                error_data = {}
    else:
        error_data = {}
    
    # Update errors
    if node_name not in error_data:
        error_data[node_name] = {}
    
    if key in error_data[node_name]:
        error_data[node_name][key] += 1
    else:
        error_data[node_name][key] = 1
    
    # Save back to file
    with open(error_file, 'w') as f:
        json.dump(error_data, f, indent=2)

def safe_rate(success, fail):
    total = success + fail
    return round((success / total) * 100, 2) if total > 0 else 0.0

def run_test_for_node(node, index):
    name = node["name"]
    print(f"\n🚀 Running test for node: {name}")

    private_key = node_keys[name]["privateKey"]
    if not private_key:
        print(f"❌ Skipping {name} — missing private key")
        return
    os.environ["PRIVATE_KEY"] = private_key

    dkg = DKG(
        NodeHTTPProvider(f"{node['hostname']}:{OT_NODE_PORT}", "v1"),
        BlockchainProvider(BLOCKCHAIN),  # Using the patched provider for Base
        {"max_number_of_retries": 90, "frequency": 2}
    )

    publish_success = query_success = local_get_success = remote_get_success = 0
    publish_fail = query_fail = local_get_fail = remote_get_fail = 0
    publish_times, query_times, local_get_times, remote_get_times = [], [], [], []
    failed_assets = []

    for i in range(10):
        print(f"\n📡 Publishing KA #{i + 1} on {name}")
        content = get_random_content(name)
        ual = None

        try:
            start = time.time()
            result = run_with_timeout(lambda: dkg.asset.create(content, {
                "epochs_num": 2,
                "minimum_number_of_finalization_confirmations": 1,
                "minimum_number_of_node_replications": 3
            }), operation_name=f"publish KA #{i + 1}")
            end = time.time()
            ual = result.get("UAL")
            assert result["operation"]["publish"]["status"] == "COMPLETED"
            assert result["operation"]["finality"]["status"] == "FINALIZED"
            assert ual
            print(f"✅ Published KA #{i + 1} with UAL: {ual}")
            publish_success += 1
            publish_times.append(end - start)
        except Exception as e:
            log_error(e, name, "publishing")
            ual = "did:dkg:otp:20430/0xcdb28e93ed340ec10a71bba00a31dbfcf1bd5d37/179542"
            print(f"⚠️ Using fallback UAL: {ual}")
            failed_assets.append(f"KA #{i + 1} (Publish failed — No UAL)")
            publish_fail += 1

        try:
            start = time.time()
            result = run_with_timeout(lambda: dkg.graph.query("""
                PREFIX schema: <http://schema.org/>
                SELECT ?s ?name ?description
                WHERE {
                    ?s schema:name ?name ; schema:description ?description .
                }
            """), operation_name=f"query KA #{i + 1}")
            end = time.time()
            assert isinstance(result, list)
            assert len(result) > 0
            print("✅ Query succeeded")
            query_success += 1
            query_times.append(end - start)
        except Exception as e:
            log_error(e, name, "querying")
            query_fail += 1
            failed_assets.append(f"KA #{i + 1} (Query failed — UAL: {ual})")

        try:
            start = time.time()
            result = run_with_timeout(lambda: dkg.asset.get(ual), operation_name=f"local get KA #{i + 1}")
            end = time.time()
            assert result and result.get("assertion")
            print("✅ Local Get Succeeded")
            local_get_success += 1
            local_get_times.append(end - start)
        except Exception as e:
            log_error(e, name, "local get")
            local_get_fail += 1
            failed_assets.append(f"KA #{i + 1} (Local Get failed — UAL: {ual})")

        other_indexes = [i for i in range(len(nodes)) if i != index]
        remote_node = nodes[random.choice(other_indexes)]
        remote_name = remote_node["name"]
        remote_key = node_keys[remote_name]["privateKey"]
        
        if not remote_key:
            print(f"⚠️ Skipping remote get - missing private key for {remote_name}")
            remote_get_fail += 1
            failed_assets.append(f"KA #{i + 1} (Remote Get failed — No private key for {remote_name})")
            continue
            
        os.environ["PRIVATE_KEY"] = remote_key

        try:
            remote_dkg = DKG(
                NodeHTTPProvider(f"{remote_node['hostname']}:{OT_NODE_PORT}", "v1"),
                BlockchainProvider(BLOCKCHAIN),  # Using the patched provider for Base
                {"max_number_of_retries": 90, "frequency": 2}
            )
            start = time.time()
            result = run_with_timeout(lambda: remote_dkg.asset.get(ual), operation_name=f"remote get KA #{i + 1} on {remote_name}")
            end = time.time()
            assert result and result.get("assertion")
            print(f"✅ Get Succeeded on {remote_name}")
            remote_get_success += 1
            remote_get_times.append(end - start)
        except Exception as e:
            log_error(e, name, "get", remote_name)
            remote_get_fail += 1
            failed_assets.append(f"KA #{i + 1} (Get failed — UAL: {ual})")

    def avg(times): return round(sum(times) / len(times), 2) if times else 0.0
    summary = {
        "blockchain_name": BLOCKCHAIN,
        "node_name": name,
        "publish_success_rate": safe_rate(publish_success, publish_fail),
        "query_success_rate": safe_rate(query_success, query_fail),
        "publisher_get_success_rate": safe_rate(local_get_success, local_get_fail),
        "non_publisher_get_success_rate": safe_rate(remote_get_success, remote_get_fail),
        "average_publish_time": avg(publish_times),
        "average_query_time": avg(query_times),
        "average_publisher_get_time": avg(local_get_times),
        "average_non_publisher_get_time": avg(remote_get_times),
        "time_stamp": datetime.utcnow().isoformat()
    }

    os.makedirs("test_output", exist_ok=True)
    with open(f"test_output/summary_{name.replace(' ', '_')}.json", "w") as f:
        json.dump(summary, f, indent=2)
    with open(f"test_output/errors_{name.replace(' ', '_')}.json", "w") as f:
        json.dump(error_stats.get(name, {}), f, indent=2)

    print(f"\n──────────── Summary for {name} ────────────")
    if failed_assets:
        print("🔍 Failed Assets:")
        for a in failed_assets:
            print(f"  - {a}")
    else:
        print("✅ All assets processed successfully")

    global_stats.setdefault(BLOCKCHAIN, {})[name] = {
        "success": publish_success,
        "failed": publish_fail,
    }
    
    # Store global stats in a file to ensure persistence across test session
    stats_file = "test_output/global_stats.json"
    os.makedirs("test_output", exist_ok=True)
    
    # Load existing stats
    if os.path.exists(stats_file):
        with open(stats_file, 'r') as f:
            try:
                stats_data = json.load(f)
            except:
                stats_data = {}
    else:
        stats_data = {}
    
    # Update stats
    if BLOCKCHAIN not in stats_data:
        stats_data[BLOCKCHAIN] = {}
    
    stats_data[BLOCKCHAIN][name] = {
        "success": publish_success,
        "failed": publish_fail,
        "publish_success": publish_success,
        "publish_failed": publish_fail,
        "query_success": query_success,
        "query_failed": query_fail,
        "local_get_success": local_get_success,
        "local_get_failed": local_get_fail,
        "remote_get_success": remote_get_success,
        "remote_get_failed": remote_get_fail,
        "publish_times": publish_times,
        "query_times": query_times,
        "local_get_times": local_get_times,
        "remote_get_times": remote_get_times,
    }
    
    # Save back to file
    with open(stats_file, 'w') as f:
        json.dump(stats_data, f, indent=2)

def get_nodes_to_test():
    """Get the list of nodes to test based on environment variable"""
    target_nodes = os.getenv("NODE_TO_TEST")
    if not target_nodes:
        return nodes  # Run all nodes if no NODE_TO_TEST specified
    
    target_list = [x.strip() for x in target_nodes.split(",")]
    nodes_to_test = []
    
    for target in target_list:
        # Check if target is a node name
        for node in nodes:
            if node["name"] == target:
                nodes_to_test.append(node)
                break
        else:
            # Check if target is a node index
            try:
                index = int(target)
                if 0 <= index < len(nodes):
                    nodes_to_test.append(nodes[index])
            except ValueError:
                print(f"⚠️ Invalid node target: {target}")
    
    return nodes_to_test

@pytest.mark.parametrize("node", get_nodes_to_test())
def test_lifecycle_per_node(node):
    run_test_for_node(node, nodes.index(node))


