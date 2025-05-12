import json
import time
import pytest
from dotenv import load_dotenv
from uuid import uuid4
import random

from dkg import DKG
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.constants import BlockchainIds

load_dotenv()

OT_NODE_PORT = 8900
BLOCKCHAIN = BlockchainIds.NEUROWEB_TESTNET.value
TOTAL_NODES = 3

# Automatically generate node hostnames
nodes = [
    {
        "name": f"Node {str(i+1).zfill(2)}",
        "hostname": f"https://v6-pegasus-node-{str(i+1).zfill(2)}.origin-trail.network"
    }
    for i in range(TOTAL_NODES)
]

words = ['Galaxy', 'Nebula', 'Orbit', 'Quantum', 'Pixel', 'Velocity', 'Echo', 'Nova']
descriptions = [
    'This asset explores the mysteries of {}.',
    'An in-depth look into {} technologies.',
    'Unlocking the power of {} in modern systems.',
    'How {} shapes our digital future.',
    'A fresh perspective on {} innovation.',
]

@pytest.mark.parametrize("node", nodes)
@pytest.mark.flaky(reruns=2, reruns_delay=5)
def test_asset_lifecycle(node):
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

    print(f"======================== NODE INFO for {node['name']}")
    #print(json.dumps(dkg.node.info, indent=4))

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

    start = time.perf_counter()
    create_asset_result = dkg.asset.create(
        content=content,
        options={
            "epochs_num": 2,
            "minimum_number_of_finalization_confirmations": 3,
            "minimum_number_of_node_replications": 1,
        },
    )
    print(f"======================== ASSET CREATED on {node['name']} in {time.perf_counter() - start:.2f}s")
    #print(json.dumps(create_asset_result, indent=4))

    ual = create_asset_result.get("UAL")
    assert ual, f"❌ UAL missing after publish on {node['name']}"
    print(f"✅ Successfully published asset on {node['name']}")

    start = time.perf_counter()
    get_result = dkg.asset.get(ual)
    print(f"======================== GET in {time.perf_counter() - start:.2f}s")
    #print(json.dumps(get_result, indent=4))
    assert get_result.get("assertion"), f"❌ Get returned no assertion on {node['name']}"
    print(f"✅ Successfully retrieved asset on {node['name']}")

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
    print(f"======================== QUERY in {time.perf_counter() - start:.2f}s")
    #print(json.dumps(query_result, indent=4))
    assert query_result, f"❌ Query returned no results on {node['name']}"
    print(f"✅ Successfully queried graph on {node['name']}")

    start = time.perf_counter()
    finality_result = dkg.graph.publish_finality(ual)
    print(f"======================== FINALITY in {time.perf_counter() - start:.2f}s")
    #print(json.dumps(finality_result, indent=4))
    assert finality_result.get("status") == "FINALIZED", f"❌ Finality not FINALIZED on {node['name']}"



