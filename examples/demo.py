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
    # "base:84532",
    # "gnosis:10200",
    "otp:20430",
    private_key="",
)

dkg = DKG(node_provider, blockchain_provider)


def divider():
    print("==================================================")
    print("==================================================")
    print("==================================================")


def print_json(json_dict: dict):
    print(json.dumps(json_dict, indent=4))


content = {}


divider()


get_v8_test = dkg.asset.get(
    "did:dkg:otp:20430/0xb4c24fc54bc811c2659c477b65da8648e499fd39/2353"
)
print("======================== ASSET FIRST STATE (GET BY STATE INDEX) RESOLVED")
print(get_v8_test)
# print_json(get_v8_test)
divider()
