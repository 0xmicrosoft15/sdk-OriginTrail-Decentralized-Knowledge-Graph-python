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

from dataclasses import dataclass
from web3 import Web3
from web3.types import TxReceipt

from dkg.dataclasses import (
    BaseIncentivesPoolParams,
    ParanetIncentivizationType,
)
from dkg.managers.manager import DefaultRequestManager
from dkg.method import Method
from dkg.modules.module import Module
from dkg.types import Address, UAL, HexStr
from dkg.utils.blockchain_request import BlockchainRequest
from dkg.utils.ual import parse_ual
from dkg.services.input_service import InputService
from dkg.services.blockchain_services.blockchain_service import BlockchainService


class Paranet(Module):
    @dataclass
    class NeuroWebIncentivesPoolParams(BaseIncentivesPoolParams):
        neuro_emission_multiplier: float
        operator_percentage: float
        voters_percentage: float

        def to_contract_args(self) -> dict:
            return {
                "trac_to_neuro_emission_multiplier": int(
                    self.neuro_emission_multiplier * (10**12)
                ),
                "paranet_operator_reward_percentage": int(
                    self.operator_percentage * 100
                ),
                "paranet_incentivization_proposal_voters_reward_percentage": int(
                    self.voters_percentage * 100
                ),
            }

    def __init__(
        self,
        manager: DefaultRequestManager,
        input_service: InputService,
        blockchain_service: BlockchainService,
    ):
        self.manager = manager
        self.input_service = input_service
        self.blockchain_service = blockchain_service

    def create(
        self,
        ual: UAL,
        options: dict = {},
    ) -> dict[str, str | HexStr | TxReceipt]:
        arguments = self.input_service.get_paranet_create_arguments(options)
        name = arguments["paranet_name"]
        description = arguments["paranet_description"]
        paranet_nodes_access_policy = arguments["paranet_nodes_access_policy"]
        paranet_miners_access_policy = arguments["paranet_miners_access_policy"]

        parsed_ual = parse_ual(ual)
        knowledge_collection_storage, knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt: TxReceipt = self.blockchain_service.register_paranet(
            knowledge_collection_storage,
            knowledge_collection_token_id,
            name,
            description,
            paranet_nodes_access_policy,
            paranet_miners_access_policy,
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_collection_storage, knowledge_collection_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _add_paranet_curated_nodes = Method(BlockchainRequest.add_paranet_curated_nodes)

    def add_curated_nodes(
        self, paranet_ual: UAL, identity_ids: list[int]
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt = self._add_paranet_curated_nodes(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            identity_ids,
        )

        return {
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [
                        paranet_knowledge_collection_storage,
                        paranet_knowledge_collection_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _remove_paranet_curated_nodes = Method(
        BlockchainRequest.remove_paranet_curated_nodes
    )

    def remove_curated_nodes(
        self, paranet_ual: UAL, identity_ids: list[int]
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt = self._remove_paranet_curated_nodes(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            identity_ids,
        )

        return {
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [
                        paranet_knowledge_collection_storage,
                        paranet_knowledge_collection_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _request_paranet_curated_node_access = Method(
        BlockchainRequest.request_paranet_curated_node_access
    )

    def request_curated_node_access(
        self, paranet_ual: UAL
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt = self._request_paranet_curated_node_access(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
        )

        return {
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [
                        paranet_knowledge_collection_storage,
                        paranet_knowledge_collection_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _approve_curated_node = Method(BlockchainRequest.approve_curated_node)

    def approve_curated_node(
        self, paranet_ual: UAL, identity_id: int
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt = self._approve_curated_node(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            identity_id,
        )

        return {
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [
                        paranet_knowledge_collection_storage,
                        paranet_knowledge_collection_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _reject_curated_node = Method(BlockchainRequest.reject_curated_node)

    def reject_curated_node(
        self, paranet_ual: UAL, identity_id: int
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt = self._reject_curated_node(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            identity_id,
        )

        return {
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [
                        paranet_knowledge_collection_storage,
                        paranet_knowledge_collection_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _get_curated_nodes = Method(BlockchainRequest.get_curated_nodes)

    def get_curated_nodes(
        self, paranet_ual: UAL
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        paranet_id = Web3.solidity_keccak(
            ["address", "uint256"],
            [
                paranet_knowledge_collection_storage,
                paranet_knowledge_collection_token_id,
            ],
        )

        return self._get_curated_nodes(paranet_id)

    _add_paranet_curated_miners = Method(BlockchainRequest.add_paranet_curated_miners)

    def add_curated_miners(
        self, paranet_ual: UAL, miner_addresses: list[Address]
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt = self._add_paranet_curated_miners(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            miner_addresses,
        )

        return {
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [
                        paranet_knowledge_collection_storage,
                        paranet_knowledge_collection_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _remove_paranet_curated_miners = Method(
        BlockchainRequest.remove_paranet_curated_miners
    )

    def remove_curated_miners(
        self, paranet_ual: UAL, miner_addresses: list[Address]
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt = self._remove_paranet_curated_miners(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            miner_addresses,
        )

        return {
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [
                        paranet_knowledge_collection_storage,
                        paranet_knowledge_collection_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _request_paranet_curated_miner_access = Method(
        BlockchainRequest.request_paranet_curated_miner_access
    )

    def request_curated_miner_access(
        self, paranet_ual: UAL
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt = self._request_paranet_curated_miner_access(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
        )

        return {
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [
                        paranet_knowledge_collection_storage,
                        paranet_knowledge_collection_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _approve_curated_miner = Method(BlockchainRequest.approve_curated_miner)

    def approve_curated_miner(
        self, paranet_ual: UAL, miner_address: Address
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt = self._approve_curated_miner(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            miner_address,
        )

        return {
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [
                        paranet_knowledge_collection_storage,
                        paranet_knowledge_collection_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _reject_curated_miner = Method(BlockchainRequest.reject_curated_miner)

    def reject_curated_miner(
        self, paranet_ual: UAL, miner_address: Address
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt = self._reject_curated_miner(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            miner_address,
        )

        return {
            "paranetUAL": paranet_ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [
                        paranet_knowledge_collection_storage,
                        paranet_knowledge_collection_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _get_knowledge_miners = Method(BlockchainRequest.get_knowledge_miners)

    def get_knowledge_miners(
        self, paranet_ual: UAL
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        paranet_id = Web3.solidity_keccak(
            ["address", "uint256"],
            [
                paranet_knowledge_collection_storage,
                paranet_knowledge_collection_token_id,
            ],
        )

        return self._get_knowledge_miners(paranet_id)

    def deploy_incentives_contract(
        self,
        paranet_ual: UAL,
        incentives_pool_parameters: NeuroWebIncentivesPoolParams,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> dict[str, str | HexStr | TxReceipt]:
        incentives_types = [item.value for item in ParanetIncentivizationType]
        if incentives_type in incentives_types:
            parsed_ual = parse_ual(paranet_ual)
            paranet_knowledge_collection_storage = parsed_ual["contract_address"]
            paranet_knowledge_collection_token_id = parsed_ual[
                "knowledge_collection_token_id"
            ]

            is_native_reward = (
                True
                if incentives_type == ParanetIncentivizationType.NEUROWEB
                else False
            )

            receipt: TxReceipt = self.blockchain_service.deploy_neuro_incentives_pool(
                is_native_reward=is_native_reward,
                paranet_knowledge_collection_storage=paranet_knowledge_collection_storage,
                paranet_knowledge_collection_token_id=paranet_knowledge_collection_token_id,
                **incentives_pool_parameters.to_contract_args(),
            )

            events = self.manager.blockchain_provider.decode_logs_event(
                receipt,
                "ParanetIncentivesPoolFactory",
                "ParanetIncetivesPoolDeployed",
            )

            return {
                "paranetUAL": paranet_ual,
                "paranetId": Web3.to_hex(
                    Web3.solidity_keccak(
                        ["address", "uint256"],
                        [
                            paranet_knowledge_collection_storage,
                            paranet_knowledge_collection_token_id,
                        ],
                    )
                ),
                "incentivesPoolContractAddress": events[0].args["incentivesPool"][
                    "addr"
                ],
                "operation": json.loads(Web3.to_json(receipt)),
            }

        raise ValueError(
            f"{incentives_type} Incentive Type isn't supported. Supported "
            f"Incentive Types: {incentives_types}"
        )

    def get_incentives_pool_address(
        self,
        paranet_ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> Address:
        parsed_ual = parse_ual(paranet_ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )
        paranet_id = Web3.solidity_keccak(
            ["address", "uint256"],
            [
                paranet_knowledge_collection_storage,
                paranet_knowledge_collection_token_id,
            ],
        )

        return self.blockchain_service.get_incentives_pool_address(
            paranet_id, incentives_type
        )

    def create_service(
        self, ual: UAL, options: dict = {}
    ) -> dict[str, str | HexStr | TxReceipt]:
        arguments = self.input_service.get_paranet_create_service_arguments(options)
        paranet_service_name = arguments["paranet_service_name"]
        paranet_service_description = arguments["paranet_service_description"]
        paranet_service_addresses = arguments["paranet_service_addresses"]

        parsed_ual = parse_ual(ual)
        knowledge_collection_storage, knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        receipt: TxReceipt = self.blockchain_service.register_paranet_service(
            knowledge_collection_storage,
            knowledge_collection_token_id,
            paranet_service_name,
            paranet_service_description,
            paranet_service_addresses,
        )

        return {
            "paranetServiceUAL": ual,
            "paranetServiceId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_collection_storage, knowledge_collection_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    def add_services(
        self, ual: UAL, services_uals: list[UAL]
    ) -> dict[str, str | HexStr | TxReceipt]:
        parsed_paranet_ual = parse_ual(ual)
        paranet_knowledge_collection_storage, paranet_knowledge_collection_token_id = (
            parsed_paranet_ual["contract_address"],
            parsed_paranet_ual["knowledge_collection_token_id"],
        )

        parsed_service_uals = []
        for service_ual in services_uals:
            parsed_service_ual = parse_ual(service_ual)
            (
                service_knowledge_collection_storage,
                service_knowledge_collection_token_id,
            ) = (
                parsed_service_ual["contract_address"],
                parsed_service_ual["knowledge_collection_token_id"],
            )

            parsed_service_uals.append(
                [
                    service_knowledge_collection_storage,
                    service_knowledge_collection_token_id,
                ]
            )

        receipt: TxReceipt = self.blockchain_service.add_paranet_services(
            paranet_knowledge_collection_storage,
            paranet_knowledge_collection_token_id,
            parsed_service_uals,
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [
                        paranet_knowledge_collection_storage,
                        paranet_knowledge_collection_token_id,
                    ],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _is_knowledge_miner_registered = Method(
        BlockchainRequest.is_knowledge_miner_registered
    )

    def is_knowledge_miner(self, ual: UAL, address: Address | None = None) -> bool:
        parsed_ual = parse_ual(ual)
        knowledge_collection_storage, knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        paranet_id = Web3.solidity_keccak(
            ["address", "uint256"],
            [knowledge_collection_storage, knowledge_collection_token_id],
        )

        return self._is_knowledge_miner_registered(
            paranet_id, address or self.manager.blockchain_provider.account.address
        )

    _owner_of = Method(BlockchainRequest.owner_of)

    def is_operator(self, ual: UAL, address: Address | None = None) -> bool:
        knowledge_collection_token_id = parse_ual(ual)["token_id"]

        return self._owner_of(knowledge_collection_token_id) == (
            address or self.manager.blockchain_provider.account.address
        )

    _is_proposal_voter = Method(BlockchainRequest.is_proposal_voter)

    def is_voter(
        self,
        ual: UAL,
        address: Address | None = None,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> bool:
        return self._is_proposal_voter(
            contract=self._get_incentives_pool_contract(ual, incentives_type),
            addr=address or self.manager.blockchain_provider.account.address,
        )

    _get_claimable_knowledge_miner_reward_amount = Method(
        BlockchainRequest.get_claimable_knowledge_miner_reward_amount
    )

    def calculate_claimable_miner_reward_amount(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> int:
        return self._get_claimable_knowledge_miner_reward_amount(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

    _get_claimable_all_knowledge_miners_reward_amount = Method(
        BlockchainRequest.get_claimable_all_knowledge_miners_reward_amount
    )

    def calculate_all_claimable_miner_rewards_amount(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> int:
        return self._get_claimable_all_knowledge_miners_reward_amount(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

    _claim_knowledge_miner_reward = Method(
        BlockchainRequest.claim_knowledge_miner_reward
    )

    def claim_miner_reward(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> dict[str, str | HexStr | TxReceipt]:
        receipt: TxReceipt = self._claim_knowledge_miner_reward(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

        parsed_ual = parse_ual(ual)
        knowledge_collection_storage, knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_collection_storage, knowledge_collection_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _get_claimable_paranet_operator_reward_amount = Method(
        BlockchainRequest.get_claimable_paranet_operator_reward_amount
    )

    def calculate_claimable_operator_reward_amount(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> int:
        return self._get_claimable_paranet_operator_reward_amount(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

    _claim_paranet_operator_reward = Method(
        BlockchainRequest.claim_paranet_operator_reward
    )

    def claim_operator_reward(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> dict[str, str | HexStr | TxReceipt]:
        receipt: TxReceipt = self._claim_paranet_operator_reward(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

        parsed_ual = parse_ual(ual)
        knowledge_collection_storage, knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_collection_storage, knowledge_collection_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    _get_claimable_proposal_voter_reward_amount = Method(
        BlockchainRequest.get_claimable_proposal_voter_reward_amount
    )

    def calculate_claimable_voter_reward_amount(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> int:
        return self._get_claimable_proposal_voter_reward_amount(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

    _get_claimable_all_proposal_voters_reward_amount = Method(
        BlockchainRequest.get_claimable_all_proposal_voters_reward_amount
    )

    def calculate_all_claimable_voters_reward_amount(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> int:
        return self._get_claimable_all_proposal_voters_reward_amount(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

    _claim_incentivization_proposal_voter_reward = Method(
        BlockchainRequest.claim_incentivization_proposal_voter_reward
    )

    def claim_voter_reward(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> dict[str, str | HexStr | TxReceipt]:
        receipt: TxReceipt = self._claim_incentivization_proposal_voter_reward(
            contract=self._get_incentives_pool_contract(ual, incentives_type)
        )

        parsed_ual = parse_ual(ual)
        knowledge_collection_storage, knowledge_collection_token_id = (
            parsed_ual["contract_address"],
            parsed_ual["knowledge_collection_token_id"],
        )

        return {
            "paranetUAL": ual,
            "paranetId": Web3.to_hex(
                Web3.solidity_keccak(
                    ["address", "uint256"],
                    [knowledge_collection_storage, knowledge_collection_token_id],
                )
            ),
            "operation": json.loads(Web3.to_json(receipt)),
        }

    def _get_incentives_pool_contract(
        self,
        ual: UAL,
        incentives_type: ParanetIncentivizationType = ParanetIncentivizationType.NEUROWEB,
    ) -> str | dict[str, str]:
        incentives_pool_name = f"Paranet{str(incentives_type)}IncentivesPool"
        is_incentives_pool_cached = (
            incentives_pool_name in self.manager.blockchain_provider.contracts.keys()
        )

        return (
            incentives_pool_name
            if is_incentives_pool_cached
            else {
                "name": incentives_pool_name,
                "address": self.get_incentives_pool_address(ual, incentives_type),
            }
        )
