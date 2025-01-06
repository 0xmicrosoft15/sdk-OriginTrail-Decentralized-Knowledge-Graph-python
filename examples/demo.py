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

from dkg import DKG
from dkg.providers import BlockchainProvider, NodeHTTPProvider

node_provider = NodeHTTPProvider("https://v6-pegasus-node-04.origin-trail.network:8900")
blockchain_provider = BlockchainProvider(
    "testnet",
    "base:84532",
    private_key="db20be6415f83a8a9f0c129bf20ab99ba15bfb90ac5e34f1848f59c20ea9c068",
)

dkg = DKG(node_provider, blockchain_provider)


def divider():
    print("==================================================")
    print("==================================================")
    print("==================================================")


def print_json(json_dict: dict):
    print(json.dumps(json_dict, indent=4))


content = {
    "public": {
        "@context": ["http://schema.org"],
        "@id": "uuid:1",
        "company": "OT",
        "user": {"@id": "uuid:user:1"},
        "city": {"@id": "uuid:belgrade"},
    },
    "private": {
        "@context": ["http://schema.org"],
        "@graph": [
            {"@id": "uuid:user:1", "name": "Adam", "lastname": "Smith"},
            {"@id": "uuid:belgrade", "title": "Belgrade", "postCode": "11000"},
        ],
    },
}


# divider()

# info_result = dkg.node.info

# print("======================== NODE INFO RECEIVED")
# print_json(info_result)

divider()

# formatted_assertions = dkg.assertion.format_graph(content)
# print("======================== ASSET FORMATTED")
# print_json(formatted_assertions)

# divider()

# public_assertion_id = dkg.assertion.get_public_assertion_id(content)
# print("======================== PUBLIC ASSERTION ID (MERKLE ROOT) CALCULATED")
# print(public_assertion_id)

# divider()

# public_assertion_size = dkg.assertion.get_size(content)
# print("======================== PUBLIC ASSERTION SIZE CALCULATED")
# print(public_assertion_size)

# divider()

# public_assertion_triples_number = dkg.assertion.get_triples_number(content)
# print("======================== PUBLIC ASSERTION TRIPLES NUMBER CALCULATED")
# print(public_assertion_triples_number)

# divider()

# public_assertion_chunks_number = dkg.assertion.get_chunks_number(content)
# print("======================== PUBLIC ASSERTION CHUNKS NUMBER CALCULATED")
# print(public_assertion_chunks_number)

# divider()

# bid_suggestion = dkg.network.get_bid_suggestion(
#     public_assertion_id,
#     public_assertion_size,
#     2,
# )
# print("======================== BID SUGGESTION CALCULATED")
# print(bid_suggestion)

# divider()

# current_allowance = dkg.asset.get_current_allowance()
# print("======================== GET CURRENT ALLOWANCE")
# print(current_allowance)

# divider()

# allowance_increase = dkg.asset.increase_allowance(bid_suggestion)
# print("======================== INCREASE ALLOWANCE")
# print(allowance_increase)

# divider()

# allowance_decrease = dkg.asset.decrease_allowance(bid_suggestion // 3)
# print("======================== DECREASE ALLOWANCE")
# print(allowance_decrease)

# divider()

# allowance_set = dkg.asset.set_allowance(bid_suggestion)
# print("======================== SET ALLOWANCE")
# print(allowance_set)

# divider()

# create_asset_result = dkg.asset.create(content, 2)
# print("======================== ASSET CREATED")
# print_json(create_asset_result)
# divider()

# validate_ual = dkg.asset.is_valid_ual(create_asset_result["UAL"])
# print("======================== VALIDATE UAL")
# print(f"Is {create_asset_result['UAL']} a valid UAL: {validate_ual}")
# divider()

# owner_result = dkg.asset.get_owner(create_asset_result["UAL"])
# print("======================== GET ASSET OWNER")
# print(owner_result)
# divider()

# get_asset_result = dkg.asset.get(create_asset_result["UAL"])
# print("======================== ASSET RESOLVED")
# print_json(get_asset_result)
# divider()

# get_latest_asset_result = dkg.asset.get(create_asset_result["UAL"], "latest", "all")
# print("======================== ASSET LATEST RESOLVED")
# print_json(get_latest_asset_result)
# divider()

# get_latest_finalized_asset_result = dkg.asset.get(
#     create_asset_result["UAL"], "latest_finalized", "all"
# )
# print("======================== ASSET LATEST FINALIZED RESOLVED")
# print_json(get_latest_finalized_asset_result)
# divider()

get_v8_test = dkg.asset.get_v8(
    "did:dkg:base:84532/0xd5550173b0f7b8766ab2770e4ba86caf714a5af5/10176"
)
print("======================== ASSET FIRST STATE (GET BY STATE INDEX) RESOLVED")
print(get_v8_test)
# print_json(get_v8_test)
divider()

# get_first_state_by_hash = dkg.asset.get(
#     create_asset_result["UAL"], create_asset_result["publicAssertionId"], "all"
# )
# print("======================== ASSET FIRST STATE (GET BY STATE HASH) RESOLVED")
# print_json(get_first_state_by_hash)
# divider()

# query_result = dkg.graph.query(
#     "construct { ?s ?p ?o } where { ?s ?p ?o . <uuid:user:1> ?p ?o }", "privateCurrent"
# )
# print("======================== QUERY LOCAL CURRENT RESULT")
# print(query_result)
