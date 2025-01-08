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
import math
import re
import hashlib
from typing import Literal, Type, Dict, Optional, Any
from pyld import jsonld
from web3 import Web3
from web3.constants import ADDRESS_ZERO
from web3.exceptions import ContractLogicError
from web3.types import TxReceipt
from itertools import chain
from eth_abi.packed import encode_packed
from eth_account.messages import encode_defunct
from eth_account import Account
from hexbytes import HexBytes

from dkg.constants import (
    DEFAULT_HASH_FUNCTION_ID,
    DEFAULT_PROXIMITY_SCORE_FUNCTIONS_PAIR_IDS,
    PRIVATE_ASSERTION_PREDICATE,
    PRIVATE_CURRENT_REPOSITORY,
    PRIVATE_HISTORICAL_REPOSITORY,
    PRIVATE_RESOURCE_PREDICATE,
    PRIVATE_HASH_SUBJECT_PREFIX,
    CHUNK_BYTE_SIZE,
    MAX_FILE_SIZE,
    Operations,
    DefaultParameters,
)
from dkg.dataclasses import (
    BidSuggestionRange,
    KnowledgeAssetContentVisibility,
    KnowledgeAssetEnumStates,
    NodeResponseDict,
)
from dkg.exceptions import (
    DatasetOutputFormatNotSupported,
    InvalidKnowledgeAsset,
    InvalidStateOption,
    InvalidTokenAmount,
    MissingKnowledgeAssetState,
    OperationNotFinished,
)
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.module import Module
from dkg.types import JSONLD, UAL, Address, AgreementData, HexStr, Wei
from dkg.utils.blockchain_request import (
    BlockchainRequest,
    KnowledgeCollectionResult,
    AllowanceResult,
)
from dkg.utils.decorators import retry
from dkg.utils.merkle import MerkleTree, hash_assertion_with_indexes
from dkg.utils.metadata import (
    generate_agreement_id,
    generate_assertion_metadata,
    generate_keyword,
)
from dkg.utils.node_request import (
    NodeRequest,
    OperationStatus,
    StoreTypes,
    validate_operation_status,
)
from dkg.utils.rdf import (
    format_content,
    normalize_dataset,
)
from dkg.utils.ual import format_ual, parse_ual
import dkg.utils.knowledge_collection_tools as kc_tools
import dkg.utils.knowledge_asset_tools as ka_tools


class KnowledgeAsset(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _owner = Method(BlockchainRequest.owner_of)

    def is_valid_ual(self, ual: UAL) -> bool:
        if not ual or not isinstance(ual, str):
            raise ValueError("UAL must be a non-empty string.")

        parts = ual.split("/")
        if len(parts) != 3:
            raise ValueError("UAL format is incorrect.")

        prefixes = parts[0].split(":")
        prefixes_number = len(prefixes)
        if prefixes_number != 3 and prefixes_number != 4:
            raise ValueError("Prefix format in UAL is incorrect.")

        if prefixes[0] != "did":
            raise ValueError(
                f"Invalid DID prefix. Expected: 'did'. Received: '{prefixes[0]}'."
            )

        if prefixes[1] != "dkg":
            raise ValueError(
                f"Invalid DKG prefix. Expected: 'dkg'. Received: '{prefixes[1]}'."
            )

        if prefixes[2] != (
            blockchain_name := (
                self.manager.blockchain_provider.blockchain_id.split(":")[0]
            )
        ):
            raise ValueError(
                "Invalid blockchain name in the UAL prefix. "
                f"Expected: '{blockchain_name}'. Received: '${prefixes[2]}'."
            )

        if prefixes_number == 4:
            chain_id = self.manager.blockchain_provider.blockchain_id.split(":")[1]

            if int(prefixes[3]) != int(chain_id):
                raise ValueError(
                    "Chain ID in UAL does not match the blockchain. "
                    f"Expected: '${chain_id}'. Received: '${prefixes[3]}'."
                )

        contract_address = self.manager.blockchain_provider.contracts[
            "ContentAssetStorage"
        ].address

        if parts[1].lower() != contract_address.lower():
            raise ValueError(
                "Contract address in UAL does not match. "
                f"Expected: '${contract_address.lower()}'. "
                f"Received: '${parts[1].lower()}'."
            )

        try:
            owner = self._owner(int(parts[2]))

            if not owner or owner == ADDRESS_ZERO:
                raise ValueError("Token does not exist or has no owner.")

            return True
        except Exception as err:
            raise ValueError(f"Error fetching asset owner: {err}")

    _get_contract_address = Method(BlockchainRequest.get_contract_address)
    _get_current_allowance = Method(BlockchainRequest.allowance)

    def get_current_allowance(self, spender: Address | None = None) -> Wei:
        if spender is None:
            spender = self._get_contract_address("ServiceAgreementV1")

        return int(
            self._get_current_allowance(
                self.manager.blockchain_provider.account.address, spender
            )
        )

    _increase_allowance = Method(BlockchainRequest.increase_allowance)
    _decrease_allowance = Method(BlockchainRequest.decrease_allowance)

    def set_allowance(self, token_amount: Wei, spender: Address | None = None) -> Wei:
        if spender is None:
            spender = self._get_contract_address("ServiceAgreementV1")

        current_allowance = self.get_current_allowance(spender)

        allowance_difference = token_amount - current_allowance

        if allowance_difference > 0:
            self._increase_allowance(spender, allowance_difference)
        elif allowance_difference < 0:
            self._decrease_allowance(spender, -allowance_difference)

        return allowance_difference

    def increase_allowance(
        self, token_amount: Wei, spender: Address | None = None
    ) -> Wei:
        if spender is None:
            spender = self._get_contract_address("ServiceAgreementV1")

        self._increase_allowance(spender, token_amount)

        return token_amount

    def decrease_allowance(
        self, token_amount: Wei, spender: Address | None = None
    ) -> Wei:
        if spender is None:
            spender = self._get_contract_address("ServiceAgreementV1")

        current_allowance = self.get_current_allowance(spender)
        subtracted_value = min(token_amount, current_allowance)

        self._decrease_allowance(spender, subtracted_value)

        return subtracted_value

    _chain_id = Method(BlockchainRequest.chain_id)

    _get_asset_storage_address = Method(BlockchainRequest.get_asset_storage_address)
    _create = Method(BlockchainRequest.create_asset)
    _mint_paranet_knowledge_asset = Method(BlockchainRequest.mint_knowledge_asset)
    _key_is_operational_wallet = Method(BlockchainRequest.key_is_operational_wallet)
    _time_until_next_epoch = Method(BlockchainRequest.time_until_next_epoch)
    _epoch_length = Method(BlockchainRequest.epoch_length)
    _get_stake_weighted_average_ask = Method(
        BlockchainRequest.get_stake_weighted_average_ask
    )
    _get_bid_suggestion = Method(NodeRequest.bid_suggestion)
    _local_store = Method(NodeRequest.local_store)
    _publish = Method(NodeRequest.publish)
    _finality_status = Method(NodeRequest.finality_status)

    _create_knowledge_collection = Method(BlockchainRequest.create_knowledge_collection)
    _mint_knowledge_asset = Method(BlockchainRequest.mint_knowledge_asset)
    _decrease_allowance = Method(BlockchainRequest.decrease_allowance)

    def get_operation_status_object(
        self, operation_result: Dict[str, Any], operation_id: str
    ) -> Dict[str, Any]:
        """
        Creates an operation status object from operation result and ID.

        Args:
            operation_result: Dictionary containing operation result data
            operation_id: The ID of the operation

        Returns:
            Dictionary containing operation status information
        """
        # Check if error_type exists in operation_result.data
        operation_data = (
            {"status": operation_result.get("status"), **operation_result.get("data")}
            if operation_result.get("data", {}).get("errorType")
            else {"status": operation_result.get("status")}
        )

        return {"operationId": operation_id, **operation_data}

    def finality_status(
        self,
        ual: str,
        required_confirmations: int,
        max_number_of_retries: int,
        frequency: int,
    ):
        retries = 0
        finality = 0

        while finality < required_confirmations and retries <= max_number_of_retries:
            if retries > max_number_of_retries:
                raise Exception(
                    f"Unable to achieve required confirmations. "
                    f"Max number of retries ({max_number_of_retries}) reached."
                )

            retries += 1

            # Sleep between attempts (except for first try)
            if retries > 1:
                time.sleep(frequency)

            try:
                response = self._finality_status(ual)
                finality = response.get("finality", 0)
            except Exception:
                finality = 0

        return finality

    def increase_knowledge_collection_allowance(
        self, sender: str, token_amount: str
    ) -> AllowanceResult:
        """
        Increases the allowance for knowledge collection if necessary.

        Args:
            sender: The address of the sender
            token_amount: The amount of tokens to check/increase allowance for

        Returns:
            AllowanceResult containing whether allowance was increased and the gap
        """
        knowledge_collection_address = self._get_contract_address("KnowledgeCollection")

        allowance = self._get_current_allowance(sender, knowledge_collection_address)
        allowance_gap = int(token_amount) - int(allowance)

        if allowance_gap > 0:
            self._increase_allowance(knowledge_collection_address, allowance_gap)

            return AllowanceResult(
                allowance_increased=True, allowance_gap=allowance_gap
            )

        return AllowanceResult(allowance_increased=False, allowance_gap=allowance_gap)

    def create_knowledge_collection(
        self,
        request: dict,
        paranet_ka_contract: Optional[Address] = None,
        paranet_token_id: Optional[int] = None,
    ) -> KnowledgeCollectionResult:
        """
        Creates a knowledge collection on the blockchain.

        Args:
            request: dict containing all collection parameters
            paranet_ka_contract: Optional paranet contract address
            paranet_token_id: Optional paranet token ID
            blockchain: Blockchain configuration

        Returns:
            KnowledgeCollectionResult containing collection ID and transaction receipt

        Raises:
            BlockchainError: If the collection creation fails
        """
        sender = self.manager.blockchain_provider.account.address
        service_agreement_v1_address = None
        allowance_increased = False
        allowance_gap = 0

        try:
            # Handle allowance
            if request.get("payer"):
                pass
            else:
                allowance_result = self.increase_knowledge_collection_allowance(
                    sender=sender,
                    token_amount=request.get("tokenAmount"),
                )
                allowance_increased = allowance_result.allowance_increased
                allowance_gap = allowance_result.allowance_gap

            if not paranet_ka_contract and not paranet_token_id:
                receipt = self._create_knowledge_collection(
                    request.get("publishOperationId"),
                    Web3.to_bytes(hexstr=request.get("merkleRoot")),
                    request.get("knowledgeAssetsAmount"),
                    request.get("byteSize"),
                    request.get("epochs"),
                    int(request.get("tokenAmount")),
                    request.get("isImmutable"),
                    request.get("paymaster"),
                    request.get("publisherNodeIdentityId"),
                    Web3.to_bytes(hexstr=request.get("publisherNodeR")),
                    Web3.to_bytes(hexstr=request.get("publisherNodeVS")),
                    request.get("identityIds"),
                    [Web3.to_bytes(hexstr=x) for x in request.get("r")],
                    [Web3.to_bytes(hexstr=x) for x in request.get("vs")],
                )
            else:
                receipt = self._mint_knowledge_asset(
                    paranet_ka_contract,
                    paranet_token_id,
                    list(request.values()),
                )

            event_data = self.manager.blockchain_provider.decode_logs_event(
                receipt=receipt,
                contract_name="KnowledgeCollectionStorage",
                event_name="KnowledgeCollectionCreated",
            )
            collection_id = (
                int(getattr(event_data[0].get("args", {}), "id", None))
                if event_data
                else None
            )

            return KnowledgeCollectionResult(
                knowledge_collection_id=collection_id, receipt=receipt
            )

        except Exception as e:
            if allowance_increased:
                self._decrease_allowance(service_agreement_v1_address, allowance_gap)
            raise e

    def process_content(self, content: str) -> list:
        return [line.strip() for line in content.split("\n") if line.strip() != ""]

    def solidity_packed_sha256(self, types: list[str], values: list) -> str:
        # Encode the values using eth_abi's encode_packed
        packed_data = encode_packed(types, values)

        # Calculate SHA256
        sha256_hash = hashlib.sha256(packed_data).hexdigest()

        return f"0x{sha256_hash}"

    def insert_triple_sorted(self, triples_list: list, new_triple: str) -> int:
        # Assuming triples_list is already sorted
        left = 0
        right = len(triples_list)

        while left < right:
            mid = (left + right) // 2
            if triples_list[mid] < new_triple:
                left = mid + 1
            else:
                right = mid

        # Insert the new triple at the correct position
        triples_list.insert(left, new_triple)
        return left

    def get_operation_status_dict(self, operation_result, operation_id):
        # Check if data exists and has errorType
        operation_data = (
            {"status": operation_result.get("status"), **operation_result.get("data")}
            if operation_result.get("data")
            and operation_result.get("data", {}).get("errorType")
            else {"status": operation_result.get("status")}
        )

        return {"operationId": operation_id, **operation_data}

    def get_message_signer_address(self, dataset_root: str, signature: dict):
        message = encode_defunct(HexBytes(dataset_root))
        r, s, v = signature.get("r"), signature.get("s"), signature.get("v")
        r = r[2:] if r.startswith("0x") else r
        s = s[2:] if s.startswith("0x") else s

        sig = "0x" + r + s + hex(v)[2:].zfill(2)

        return Account.recover_message(message, signature=sig)

    def create(
        self,
        content: dict[Literal["public", "private"], JSONLD],
        epochs_num: int,
        minimum_number_of_finalization_confirmations: int,
        minimum_number_of_node_replications: int,
        token_amount: Wei | None = None,
    ) -> dict[str, UAL | HexStr | dict[str, dict[str, str] | TxReceipt]]:
        blockchain_id = self.manager.blockchain_provider.blockchain_id

        dataset = {}
        public_content = dataset.get("public")
        private_content = dataset.get("private")
        if isinstance(content, str):
            dataset["public"] = self.process_content(content)
        elif isinstance(public_content, str) or (
            not public_content and private_content and isinstance(private_content, str)
        ):
            if public_content:
                dataset["public"] = self.process_content(public_content)
            else:
                dataset["public"] = []

            if private_content and isinstance(private_content, str):
                dataset["private"] = self.process_content(private_content)
        else:
            dataset = kc_tools.format_dataset(content)

        public_triples_grouped = []

        dataset["public"] = kc_tools.generate_missing_ids_for_blank_nodes(
            dataset.get("public")
        )

        if dataset.get("private") and len(dataset.get("private")):
            dataset["private"] = kc_tools.generate_missing_ids_for_blank_nodes(
                dataset.get("private")
            )

            # Group private triples by subject and flatten
            private_triples_grouped = kc_tools.group_nquads_by_subject(
                dataset.get("private"), True
            )

            dataset["private"] = list(chain.from_iterable(private_triples_grouped))

            # Compute private root and add to public
            private_root = kc_tools.calculate_merkle_root(dataset.get("private"))
            dataset["public"].append(
                f'<{ka_tools.generate_named_node()}> <{PRIVATE_ASSERTION_PREDICATE}> "{private_root}" .'
            )

            # Compute private root and add to public
            public_triples_grouped = kc_tools.group_nquads_by_subject(
                dataset.get("public"), True
            )

            # Create a dictionary for public subject -> index for quick lookup
            public_subject_dict = {}
            for i in range(len(public_triples_grouped)):
                public_subject = public_triples_grouped[i][0].split(" ")[0]
                public_subject_dict[public_subject] = i

            private_triple_subject_hashes_grouped_without_public_pair = []

            # Integrate private subjects into public or store separately if no match to be appended later
            for private_triples in private_triples_grouped:
                private_subject = private_triples[0].split(" ")[
                    0
                ]  # Extract the private subject

                private_subject_hash = self.solidity_packed_sha256(
                    types=["string"],
                    values=[private_subject[1:-1]],
                )

                if (
                    private_subject in public_subject_dict
                ):  # Check if there's a public pair
                    # If there's a public pair, insert a representation in that group
                    public_index = public_subject_dict.get(private_subject)
                    self.insert_triple_sorted(
                        public_triples_grouped[public_index],
                        f"{private_subject} <{PRIVATE_RESOURCE_PREDICATE}> <{ka_tools.generate_named_node()}> .",
                    )
                else:
                    # If no public pair, maintain separate list, inserting sorted by hash
                    self.insert_triple_sorted(
                        private_triple_subject_hashes_grouped_without_public_pair,
                        f"<{PRIVATE_HASH_SUBJECT_PREFIX}{private_subject_hash}> <{PRIVATE_RESOURCE_PREDICATE}> <{ka_tools.generate_named_node()}> .",
                    )

            for triple in private_triple_subject_hashes_grouped_without_public_pair:
                public_triples_grouped.append([triple])

            dataset["public"] = list(chain.from_iterable(public_triples_grouped))
        else:
            # No private triples, just group and flatten public
            public_triples_grouped = kc_tools.group_nquads_by_subject(
                dataset.get("public"), True
            )
            dataset["public"] = list(chain.from_iterable(public_triples_grouped))

        # Calculate the number of chunks
        number_of_chunks = kc_tools.calculate_number_of_chunks(
            dataset.get("public"), CHUNK_BYTE_SIZE
        )
        dataset_size = number_of_chunks * CHUNK_BYTE_SIZE

        # Validate the assertion size in bytes
        if dataset_size > MAX_FILE_SIZE:
            raise ValueError(f"File size limit is {MAX_FILE_SIZE / (1024 * 1024)}MB.")

        # Calculate the Merkle root
        dataset_root = kc_tools.calculate_merkle_root(dataset.get("public"))

        # Get the contract address for KnowledgeCollectionStorage
        content_asset_storage_address = self._get_asset_storage_address(
            "KnowledgeCollectionStorage"
        )

        publish_operation_id = self._publish(
            dataset_root,
            dataset,
            blockchain_id,
            DEFAULT_HASH_FUNCTION_ID,
            minimum_number_of_node_replications,
        )["operationId"]
        publish_operation_result = self.get_operation_result(
            Operations.PUBLISH.value,
            publish_operation_id,
        )

        if publish_operation_result.get(
            "status"
        ) != OperationStatus.COMPLETED and not publish_operation_result.get(
            "data", {}
        ).get("minAcksReached"):
            return {
                "datasetRoot": dataset_root,
                "operation": {
                    "publish": self.get_operation_status_dict(
                        publish_operation_result, publish_operation_id
                    )
                },
            }

        data = publish_operation_result.get("data", {})
        signatures = data.get("signatures")

        publisher_node_signature = data.get("publisherNodeSignature", {})
        publisher_node_identity_id = publisher_node_signature.get("identityId")
        publisher_node_r = publisher_node_signature.get("r")
        publisher_node_vs = publisher_node_signature.get("vs")

        identity_ids, r, vs = [], [], []

        for signature in signatures:
            try:
                signer_address = self.get_message_signer_address(
                    dataset_root, signature
                )

                key_is_operational_wallet = self._key_is_operational_wallet(
                    signature.get("identityId"),
                    Web3.solidity_keccak(["address"], [signer_address]),
                    2,  # IdentityLib.OPERATIONAL_KEY
                )

                # If valid, append the signature components
                if key_is_operational_wallet:
                    identity_ids.append(signature.get("identityId"))
                    r.append(signature.get("r"))
                    vs.append(signature.get("vs"))

            except Exception:
                continue

        if token_amount:
            estimated_publishing_cost = token_amount
        else:
            time_until_next_epoch = self._time_until_next_epoch()
            epoch_length = self._epoch_length()
            stake_weighted_average_ask = self._get_stake_weighted_average_ask()

            # Convert to integers and perform calculation
            # Note: In Python we use regular int as it handles arbitrary precision automatically
            estimated_publishing_cost = (
                (
                    int(stake_weighted_average_ask)
                    * (
                        int(epochs_num) * int(1e18)
                        + (int(time_until_next_epoch) * int(1e18)) / int(epoch_length)
                    )
                    * int(dataset_size)
                )
                / 1024
                / int(1e18)
            )

        knowledge_collection_id = None
        mint_knowledge_asset_receipt = None

        knowledge_collection_result = self.create_knowledge_collection(
            {
                "publishOperationId": publish_operation_id,
                "merkleRoot": dataset_root,
                "knowledgeAssetsAmount": kc_tools.count_distinct_subjects(
                    dataset.get("public")
                ),
                "byteSize": dataset_size,
                "epochs": epochs_num,
                "tokenAmount": str(estimated_publishing_cost),
                "isImmutable": DefaultParameters.IMMUTABLE.value,
                "paymaster": DefaultParameters.ZERO_ADDRESS.value,
                "publisherNodeIdentityId": publisher_node_identity_id,
                "publisherNodeR": publisher_node_r,
                "publisherNodeVS": publisher_node_vs,
                "identityIds": identity_ids,
                "r": r,
                "vs": vs,
            },
            None,
            None,
        )
        knowledge_collection_id = knowledge_collection_result.knowledge_collection_id
        mint_knowledge_asset_receipt = knowledge_collection_result.receipt

        ual = format_ual(
            blockchain_id, content_asset_storage_address, knowledge_collection_id
        )

        finality_status_result = 0
        if minimum_number_of_finalization_confirmations > 0:
            finality_status_result = self.finality_status(
                ual,
                minimum_number_of_finalization_confirmations,
                300,
                2,
            )

        return json.loads(
            Web3.to_json(
                {
                    "UAL": ual,
                    "datasetRoot": dataset_root,
                    "signatures": publish_operation_result.get("data", {}).get(
                        "signatures"
                    ),
                    "operation": {
                        "mintKnowledgeAsset": mint_knowledge_asset_receipt,
                        "publish": self.get_operation_status_object(
                            publish_operation_result, publish_operation_id
                        ),
                        "finality": {
                            "status": "FINALIZED"
                            if finality_status_result
                            >= minimum_number_of_finalization_confirmations
                            else "NOT FINALIZED"
                        },
                        "numberOfConfirmations": finality_status_result,
                        "requiredConfirmations": minimum_number_of_finalization_confirmations,
                    },
                }
            )
        )

    def local_store(
        self,
        content: dict[Literal["public", "private"], JSONLD],
        epochs_number: int,
        token_amount: Wei | None = None,
        immutable: bool = False,
        content_type: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
        paranet_ual: UAL | None = None,
    ) -> dict[str, UAL | HexStr | dict[str, dict[str, str] | TxReceipt]]:
        blockchain_id = self.manager.blockchain_provider.blockchain_id
        assertions = format_content(content, content_type)

        public_assertion_id = MerkleTree(
            hash_assertion_with_indexes(assertions["public"]),
            sort_pairs=True,
        ).root
        public_assertion_metadata = generate_assertion_metadata(assertions["public"])

        content_asset_storage_address = self._get_asset_storage_address(
            "ContentAssetStorage"
        )

        if token_amount is None:
            token_amount = int(
                self._get_bid_suggestion(
                    blockchain_id,
                    epochs_number,
                    public_assertion_metadata["size"],
                    content_asset_storage_address,
                    public_assertion_id,
                    DEFAULT_HASH_FUNCTION_ID,
                    token_amount or BidSuggestionRange.LOW,
                )["bidSuggestion"]
            )

        current_allowance = self.get_current_allowance()
        if is_allowance_increased := current_allowance < token_amount:
            self.increase_allowance(token_amount)

        result = {"publicAssertionId": public_assertion_id, "operation": {}}

        try:
            receipt: TxReceipt = self._create(
                {
                    "assertionId": Web3.to_bytes(hexstr=public_assertion_id),
                    "size": public_assertion_metadata["size"],
                    "triplesNumber": public_assertion_metadata["triples_number"],
                    "chunksNumber": public_assertion_metadata["chunks_number"],
                    "tokenAmount": token_amount,
                    "epochsNumber": epochs_number,
                    "scoreFunctionId": DEFAULT_PROXIMITY_SCORE_FUNCTIONS_PAIR_IDS[
                        self.manager.blockchain_provider.environment
                    ][blockchain_id],
                    "immutable_": immutable,
                }
            )
        except ContractLogicError as err:
            if is_allowance_increased:
                self.decrease_allowance(token_amount)
            raise err

        events = self.manager.blockchain_provider.decode_logs_event(
            receipt,
            "ContentAsset",
            "AssetMinted",
        )
        token_id = events[0].args["tokenId"]

        result["UAL"] = format_ual(
            blockchain_id, content_asset_storage_address, token_id
        )
        result["operation"]["mintKnowledgeAsset"] = json.loads(Web3.to_json(receipt))

        assertions_list = [
            {
                "blockchain": blockchain_id,
                "contract": content_asset_storage_address,
                "tokenId": token_id,
                "assertionId": public_assertion_id,
                "assertion": assertions["public"],
                "storeType": StoreTypes.TRIPLE_PARANET,
                "paranetUAL": paranet_ual,
            }
        ]

        if content.get("private", None):
            assertions_list.append(
                {
                    "blockchain": blockchain_id,
                    "contract": content_asset_storage_address,
                    "tokenId": token_id,
                    "assertionId": MerkleTree(
                        hash_assertion_with_indexes(assertions["private"]),
                        sort_pairs=True,
                    ).root,
                    "assertion": assertions["private"],
                    "storeType": StoreTypes.TRIPLE_PARANET,
                    "paranetUAL": paranet_ual,
                }
            )

        operation_id = self._local_store(assertions_list)["operationId"]
        operation_result = self.get_operation_result(operation_id, "local-store")

        result["operation"]["localStore"] = {
            "operationId": operation_id,
            "status": operation_result["status"],
        }

        if operation_result["status"] == OperationStatus.COMPLETED:
            parsed_paranet_ual = parse_ual(paranet_ual)
            paranet_knowledge_asset_storage, paranet_knowledge_asset_token_id = (
                parsed_paranet_ual["contract_address"],
                parsed_paranet_ual["token_id"],
            )

            receipt: TxReceipt = self._submit_knowledge_asset(
                paranet_knowledge_asset_storage,
                paranet_knowledge_asset_token_id,
                content_asset_storage_address,
                token_id,
            )

            result["operation"]["submitToParanet"] = json.loads(Web3.to_json(receipt))

        return result

    _submit_knowledge_asset = Method(BlockchainRequest.submit_knowledge_asset)

    def submit_to_paranet(
        self, ual: UAL, paranet_ual: UAL
    ) -> dict[str, UAL | Address | TxReceipt]:
        parsed_ual = parse_ual(ual)
        knowledge_asset_storage, knowledge_asset_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        parsed_paranet_ual = parse_ual(paranet_ual)
        paranet_knowledge_asset_storage, paranet_knowledge_asset_token_id = (
            parsed_paranet_ual["contract_address"],
            parsed_paranet_ual["token_id"],
        )

        receipt: TxReceipt = self._submit_knowledge_asset(
            paranet_knowledge_asset_storage,
            paranet_knowledge_asset_token_id,
            knowledge_asset_storage,
            knowledge_asset_token_id,
        )

        return {
            "UAL": ual,
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_asset_storage, knowledge_asset_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _transfer = Method(BlockchainRequest.transfer_asset)

    def transfer(
        self,
        ual: UAL,
        new_owner: Address,
    ) -> dict[str, UAL | Address | TxReceipt]:
        token_id = parse_ual(ual)["token_id"]

        receipt: TxReceipt = self._transfer(
            self.manager.blockchain_provider.account,
            new_owner,
            token_id,
        )

        return {
            "UAL": ual,
            "owner": new_owner,
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _burn_asset = Method(BlockchainRequest.burn_asset)

    def burn(self, ual: UAL) -> dict[str, UAL | TxReceipt]:
        token_id = parse_ual(ual)["token_id"]

        receipt: TxReceipt = self._burn_asset(token_id)

        return {"UAL": ual, "operation": json.loads(Web3.to_json(receipt))}

    _get_assertion_ids = Method(BlockchainRequest.get_assertion_ids)
    _get_latest_assertion_id = Method(BlockchainRequest.get_latest_assertion_id)
    _get_unfinalized_state = Method(BlockchainRequest.get_unfinalized_state)

    _get = Method(NodeRequest.get)
    _query = Method(NodeRequest.query)

    def get(
        self,
        ual: UAL,
        state: str | HexStr | int = KnowledgeAssetEnumStates.LATEST,
        content_visibility: str = KnowledgeAssetContentVisibility.ALL,
        output_format: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
        validate: bool = True,
    ) -> dict[str, UAL | HexStr | list[JSONLD] | dict[str, str]]:
        state = (
            state.upper()
            if (isinstance(state, str) and not re.match(r"^0x[a-fA-F0-9]{64}$", state))
            else state
        )
        content_visibility = content_visibility.upper()
        output_format = output_format.upper()

        token_id = parse_ual(ual)["token_id"]

        def handle_latest_finalized_state(token_id: int) -> tuple[HexStr, bool]:
            return Web3.to_hex(self._get_latest_assertion_id(token_id)), True

        is_state_finalized = False

        match state:
            case (
                KnowledgeAssetEnumStates.LATEST
                | KnowledgeAssetEnumStates.LATEST_FINALIZED
            ):
                public_assertion_id, is_state_finalized = handle_latest_finalized_state(
                    token_id
                )

            case _ if isinstance(state, int):
                assertion_ids = [
                    Web3.to_hex(assertion_id)
                    for assertion_id in self._get_assertion_ids(token_id)
                ]
                if 0 <= state < (states_number := len(assertion_ids)):
                    public_assertion_id = assertion_ids[state]

                    if state == states_number - 1:
                        is_state_finalized = True
                else:
                    raise InvalidStateOption(f"State index {state} is out of range.")

            case _ if isinstance(state, str) and re.match(
                r"^0x[a-fA-F0-9]{64}$", state
            ):
                assertion_ids = [
                    Web3.to_hex(assertion_id)
                    for assertion_id in self._get_assertion_ids(token_id)
                ]

                if state in assertion_ids:
                    public_assertion_id = state

                    if state == assertion_ids[-1]:
                        is_state_finalized = True
                else:
                    raise InvalidStateOption(
                        f"Given state hash: {state} is not a part of the KA."
                    )

            case _:
                raise InvalidStateOption(f"Invalid state option: {state}.")

        get_public_operation_id: NodeResponseDict = self._get(
            ual, public_assertion_id, hashFunctionId=1
        )["operationId"]

        get_public_operation_result = self.get_operation_result(
            get_public_operation_id, "get"
        )
        public_assertion = get_public_operation_result["data"].get("assertion", None)

        if public_assertion is None:
            raise MissingKnowledgeAssetState("Unable to find state on the network!")

        if validate:
            root = MerkleTree(
                hash_assertion_with_indexes(public_assertion), sort_pairs=True
            ).root
            if root != public_assertion_id:
                raise InvalidKnowledgeAsset(
                    f"State: {public_assertion_id}. " f"Merkle Tree Root: {root}"
                )

        result = {"operation": {}}
        if content_visibility != KnowledgeAssetContentVisibility.PRIVATE:
            formatted_public_assertion = public_assertion

            match output_format:
                case "NQUADS" | "N-QUADS":
                    formatted_public_assertion: list[JSONLD] = jsonld.from_rdf(
                        "\n".join(public_assertion),
                        {"algorithm": "URDNA2015", "format": "application/n-quads"},
                    )
                case "JSONLD" | "JSON-LD":
                    formatted_public_assertion = "\n".join(public_assertion)

                case _:
                    raise DatasetOutputFormatNotSupported(
                        f"{output_format} isn't supported!"
                    )

            if content_visibility == KnowledgeAssetContentVisibility.PUBLIC:
                result = {
                    **result,
                    "asertion": formatted_public_assertion,
                    "assertionId": public_assertion_id,
                }
            else:
                result["public"] = {
                    "assertion": formatted_public_assertion,
                    "assertionId": public_assertion_id,
                }

            result["operation"]["publicGet"] = {
                "operationId": get_public_operation_id,
                "status": get_public_operation_result["status"],
            }

        if content_visibility != KnowledgeAssetContentVisibility.PUBLIC:
            private_assertion_link_triples = list(
                filter(
                    lambda element: PRIVATE_ASSERTION_PREDICATE in element,
                    public_assertion,
                )
            )

            if private_assertion_link_triples:
                private_assertion_id = re.search(
                    r'"(.*?)"', private_assertion_link_triples[0]
                ).group(1)

                private_assertion = get_public_operation_result["data"].get(
                    "privateAssertion", None
                )

                query_private_operation_id: NodeResponseDict | None = None
                if private_assertion is None:
                    query = f"""
                    CONSTRUCT {{ ?s ?p ?o }}
                    WHERE {{
                        {{
                            GRAPH <assertion:{private_assertion_id}>
                            {{
                                ?s ?p ?o .
                            }}
                        }}
                    }}
                    """

                    query_private_operation_id = self._query(
                        query,
                        "CONSTRUCT",
                        PRIVATE_CURRENT_REPOSITORY
                        if is_state_finalized
                        else PRIVATE_HISTORICAL_REPOSITORY,
                    )["operationId"]

                    query_private_operation_result = self.get_operation_result(
                        query_private_operation_id, "query"
                    )

                    private_assertion = normalize_dataset(
                        query_private_operation_result["data"],
                        "N-Quads",
                    )

                    if validate:
                        root = MerkleTree(
                            hash_assertion_with_indexes(private_assertion),
                            sort_pairs=True,
                        ).root
                        if root != private_assertion_id:
                            raise InvalidKnowledgeAsset(
                                f"State: {private_assertion_id}. "
                                f"Merkle Tree Root: {root}"
                            )

                    match output_format:
                        case "NQUADS" | "N-QUADS":
                            formatted_private_assertion: list[JSONLD] = jsonld.from_rdf(
                                "\n".join(private_assertion),
                                {
                                    "algorithm": "URDNA2015",
                                    "format": "application/n-quads",
                                },
                            )
                        case "JSONLD" | "JSON-LD":
                            formatted_private_assertion = "\n".join(private_assertion)

                        case _:
                            raise DatasetOutputFormatNotSupported(
                                f"{output_format} isn't supported!"
                            )

                    if content_visibility == KnowledgeAssetContentVisibility:
                        result = {
                            **result,
                            "assertion": formatted_private_assertion,
                            "assertionId": private_assertion_id,
                        }
                    else:
                        result["private"] = {
                            "assertion": formatted_private_assertion,
                            "assertionId": private_assertion_id,
                        }

                    if query_private_operation_id is not None:
                        result["operation"]["queryPrivate"] = {
                            "operationId": query_private_operation_id,
                            "status": query_private_operation_result["status"],
                        }

        return result

    _extend_storing_period = Method(BlockchainRequest.extend_asset_storing_period)

    def extend_storing_period(
        self,
        ual: UAL,
        additional_epochs: int,
        token_amount: Wei | None = None,
    ) -> dict[str, UAL | TxReceipt]:
        parsed_ual = parse_ual(ual)
        blockchain_id, content_asset_storage_address, token_id = (
            parsed_ual["blockchain"],
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        if token_amount is None:
            latest_finalized_state = self._get_latest_assertion_id(token_id)
            latest_finalized_state_size = self._get_assertion_size(
                latest_finalized_state
            )

            token_amount = int(
                self._get_bid_suggestion(
                    blockchain_id,
                    additional_epochs,
                    latest_finalized_state_size,
                    content_asset_storage_address,
                    latest_finalized_state,
                    DEFAULT_HASH_FUNCTION_ID,
                    token_amount or BidSuggestionRange.LOW,
                )["bidSuggestion"]
            )

        receipt: TxReceipt = self._extend_storing_period(
            token_id, additional_epochs, token_amount
        )

        return {
            "UAL": ual,
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _get_block = Method(BlockchainRequest.get_block)

    _get_service_agreement_data = Method(BlockchainRequest.get_service_agreement_data)
    _get_assertion_size = Method(BlockchainRequest.get_assertion_size)
    _add_tokens = Method(BlockchainRequest.increase_asset_token_amount)

    def add_tokens(
        self,
        ual: UAL,
        token_amount: Wei | None = None,
    ) -> dict[str, UAL | TxReceipt]:
        parsed_ual = parse_ual(ual)
        blockchain_id, content_asset_storage_address, token_id = (
            parsed_ual["blockchain"],
            parsed_ual["contract_address"],
            parsed_ual["token_id"],
        )

        if token_amount is None:
            agreement_id = self.get_agreement_id(
                content_asset_storage_address, token_id
            )
            # TODO: Dynamic types for namedtuples?
            agreement_data: Type[AgreementData] = self._get_service_agreement_data(
                agreement_id
            )

            timestamp_now = self._get_block("latest")["timestamp"]
            current_epoch = math.floor(
                (timestamp_now - agreement_data.startTime) / agreement_data.epochLength
            )
            epochs_left = agreement_data.epochsNumber - current_epoch

            latest_finalized_state = self._get_latest_assertion_id(token_id)
            latest_finalized_state_size = self._get_assertion_size(
                latest_finalized_state
            )

            token_amount = int(
                self._get_bid_suggestion(
                    blockchain_id,
                    epochs_left,
                    latest_finalized_state_size,
                    content_asset_storage_address,
                    latest_finalized_state,
                    DEFAULT_HASH_FUNCTION_ID,
                    token_amount or BidSuggestionRange.LOW,
                )["bidSuggestion"]
            ) - sum(agreement_data.tokensInfo)

            if token_amount <= 0:
                raise InvalidTokenAmount(
                    "Token amount is bigger than default suggested amount, "
                    "please specify exact token_amount if you still want to add "
                    "more tokens!"
                )

        receipt: TxReceipt = self._add_tokens(token_id, token_amount)

        return {
            "UAL": ual,
            "operation": json.loads(Web3.to_json(receipt)),
        }

    def get_owner(self, ual: UAL) -> Address:
        token_id = parse_ual(ual)["token_id"]

        return self._owner(token_id)

    _get_assertion_id_by_index = Method(BlockchainRequest.get_assertion_id_by_index)

    def get_agreement_id(self, contract_address: Address, token_id: int) -> HexStr:
        first_assertion_id = self._get_assertion_id_by_index(token_id, 0)
        keyword = generate_keyword(contract_address, first_assertion_id)
        return generate_agreement_id(contract_address, token_id, keyword)

    _get_operation_result = Method(NodeRequest.get_operation_result)

    @retry(
        catch=OperationNotFinished,
        max_retries=DefaultParameters.MAX_NUMBER_OF_RETRIES.value,
        base_delay=DefaultParameters.FREQUENCY.value,
        backoff=2,
    )
    def get_operation_result(
        self, operation: str, operation_id: str
    ) -> NodeResponseDict:
        operation_result = self._get_operation_result(
            operation=operation,
            operation_id=operation_id,
        )

        validate_operation_status(operation_result)

        return operation_result
