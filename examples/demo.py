# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import json
import time

from dkg import DKG
from dkg.providers import BlockchainProvider, NodeHTTPProvider
from dkg.constants import Environments, Blockchains

node_provider = NodeHTTPProvider(endpoint_uri="http://localhost:8900", api_version="v1")
blockchain_provider = BlockchainProvider(
    Environments.DEVELOPMENT.value,
    Blockchains.HARDHAT_1.value,
)

dkg = DKG(node_provider, blockchain_provider)


def divider():
    print("==================================================")
    print("==================================================")
    print("==================================================")


def print_json(json_dict: dict):
    print(json.dumps(json_dict, indent=4))


content = {
    "private": {
        "@context": "https://www.schema.org",
        "@id": "urn:eu-pp:safety-test:3oRIwPtUOJapwNSAGZTzCOWR9bEo",
        "@type": "ProductSafetyTest",
        "testType": "Functional Safety Test",
        "testResults": "Fail",
        "relatedProduct": [
            {
                "@id": "urn:epc:id:sgtin:59G1yu8uivSRKLLu",
                "name": "59G1yu8uivSRKLLu",
            },
        ],
    },
}


divider()

info_result = dkg.node.info

print("======================== NODE INFO RECEIVED")
print_json(info_result)

divider()

start_time = time.time()
create_asset_result = dkg.asset.create(
    content=content,
    options={
        "epochs_num": 2,
        "minimum_number_of_finalization_confirmations": 3,
        "minimum_number_of_node_replications": 1,
        "token_amount": 100,
    },
)
print(f"======================== ASSET CREATED in {time.time() - start_time} seconds")
print_json(create_asset_result)

divider()

start_time = time.time()
get_v8_test = dkg.asset.get(create_asset_result.get("UAL"))
print(f"======================== ASSET GET in {time.time() - start_time} seconds")
print_json(get_v8_test)

divider()

query_operation_result = dkg.graph.query(
    """
    PREFIX gs1: <https://gs1.org/voc/>
    PREFIX schema: <http://schema.org/>
    SELECT ?recipeNameRaw ?baseUal
    WHERE {
        ?recipe a schema:Recipe ;
        GRAPH ?ual {
            ?recipe     schema:name ?recipeNameRaw ;
        }
        FILTER (STRSTARTS(STR(?ual), "did:dkg:base:84532/0x4e8ebfce9a0f4be374709f1ef2791e8ca6371ecb/"))
        BIND (REPLACE(STR(?ual), "(did:dkg:base:[^/]+/[^/]+/[^/]+)(/.*)?", "$1") AS ?baseUal)
    }
    """
)
print("======================== ASSET QUERY")
print(query_operation_result)

divider()

query_operation_result = dkg.graph.query(
    """
    CONSTRUCT { ?s ?p ?o .}
    WHERE {
        GRAPH ?g { ?s ?p ?o . } 
        VALUES ?g {
            <did:dkg:gnosis:10200/0xcdd5ce31fe2181490348ef6fd9f782d575776e5b/4/1/public>
            <did:dkg:gnosis:10200/0xcdd5ce31fe2181490348ef6fd9f782d575776e5b/4/2/public>
        }
    }
    """
)
print("======================== ASSET QUERY")
print(query_operation_result)

divider()

query_operation_result = dkg.graph.query(
    """
    CONSTRUCT { ?s ?p ?o . }
    WHERE {
        {
            GRAPH <did:dkg:gnosis:10200/0xcdd5ce31fe2181490348ef6fd9f782d575776e5b/4/1/public> { ?s ?p ?o . }  
        }
        UNION
        {
            GRAPH <did:dkg:gnosis:10200/0xcdd5ce31fe2181490348ef6fd9f782d575776e5b/4/2/public> { ?s ?p ?o . }
        }
    }
    """
)
print("======================== ASSET QUERY")
print(query_operation_result)
