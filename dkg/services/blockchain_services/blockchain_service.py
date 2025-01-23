from dkg.modules.module import Module
from dkg.managers.manager import DefaultRequestManager
from dkg.utils.blockchain_request import BlockchainRequest
from dkg.method import Method
from dkg.constants import ZERO_ADDRESS
from web3 import Web3
from typing import Optional
from dkg.types import Address, UAL
from dkg.utils.blockchain_request import KnowledgeCollectionResult, AllowanceResult
from dkg.utils.ual import parse_ual


class BlockchainService(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _owner = Method(BlockchainRequest.owner_of)
    _get_contract_address = Method(BlockchainRequest.get_contract_address)
    _get_current_allowance = Method(BlockchainRequest.allowance)
    _increase_allowance = Method(BlockchainRequest.increase_allowance)
    _decrease_allowance = Method(BlockchainRequest.decrease_allowance)
    _create_knowledge_collection = Method(BlockchainRequest.create_knowledge_collection)
    _mint_knowledge_collection = Method(BlockchainRequest.mint_knowledge_collection)
    _get_asset_storage_address = Method(BlockchainRequest.get_asset_storage_address)
    _key_is_operational_wallet = Method(BlockchainRequest.key_is_operational_wallet)
    _time_until_next_epoch = Method(BlockchainRequest.time_until_next_epoch)
    _epoch_length = Method(BlockchainRequest.epoch_length)
    _get_stake_weighted_average_ask = Method(
        BlockchainRequest.get_stake_weighted_average_ask
    )
    _get_block = Method(BlockchainRequest.get_block)

    def decrease_knowledge_collection_allowance(
        self,
        allowance_gap: int,
    ):
        knowledge_collection_address = self._get_contract_address("KnowledgeCollection")
        self._decrease_allowance(knowledge_collection_address, allowance_gap)

    def increase_knowledge_collection_allowance(
        self,
        sender: str,
        token_amount: str,
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
        allowance_increased = False
        allowance_gap = 0

        try:
            # Handle allowance
            if request.get("paymaster") and request.get("paymaster") != ZERO_ADDRESS:
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
                    request.get("tokenAmount"),
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
                receipt = self._mint_knowledge_collection(
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
                self.decrease_knowledge_collection_allowance(allowance_gap)
            raise e

    # TODO: change self._owner to v8 compatible function
    def get_owner(self, ual: UAL) -> Address:
        token_id = parse_ual(ual)["token_id"]

        return self._owner(token_id)

    def get_asset_storage_address(self, asset_storage_name: str) -> Address:
        return self._get_asset_storage_address(asset_storage_name)

    def key_is_operational_wallet(
        self, identity_id: int, key: Address, purpose: int
    ) -> bool:
        return self._key_is_operational_wallet(identity_id, key, purpose)

    def time_until_next_epoch(self) -> int:
        return self._time_until_next_epoch()

    def epoch_length(self) -> int:
        return self._epoch_length()

    def get_stake_weighted_average_ask(self) -> int:
        return self._get_stake_weighted_average_ask()

    def get_block(self, block_identifier: str | int):
        return self._get_block(block_identifier)
