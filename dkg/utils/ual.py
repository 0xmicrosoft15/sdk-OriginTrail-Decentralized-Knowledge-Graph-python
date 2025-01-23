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

from dkg.exceptions import ValidationError
from dkg.types import UAL, Address, ChecksumAddress
from web3 import Web3


def format_ual(
    blockchain: str,
    contract_address: Address | ChecksumAddress,
    knowledge_collection_token_id: int,
    knowledge_asset_token_id: int | None = None,
) -> UAL:
    ual = f"did:dkg:{blockchain.lower()}/{contract_address.lower()}/{knowledge_collection_token_id}"
    return f"{ual}/{knowledge_asset_token_id}" if knowledge_asset_token_id else ual


def parse_ual(ual: UAL) -> dict[str, str | Address | int]:
    if not ual.startswith("did:dkg:"):
        raise ValidationError("Invalid UAL!")

    args = ual.replace("did:dkg:", "").split("/")

    knowledge_asset_token_id = None
    if len(args) == 4:
        (
            blockchain,
            contract_address,
            knowledge_collection_token_id,
            knowledge_asset_token_id,
        ) = args
    elif len(args) == 3:
        blockchain, contract_address, knowledge_collection_token_id = args
    else:
        raise ValidationError("Invalid UAL!")

    resolved_ual = {
        "blockchain": blockchain,
        "contract_address": Web3.to_checksum_address(contract_address),
        "knowledge_collection_token_id": int(knowledge_collection_token_id),
    }

    if knowledge_asset_token_id:
        resolved_ual["knowledge_asset_token_id"] = int(knowledge_asset_token_id)

    return resolved_ual
