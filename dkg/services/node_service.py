from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.constants import OperationStatuses
from dkg.utils.node_request import NodeRequest
from dkg.module import Module
from typing import Dict, Any
from dkg.types import UAL
import asyncio


class NodeService(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _get_operation_result = Method(NodeRequest.get_operation_result)
    _finality_status = Method(NodeRequest.finality_status)
    _finality = Method(NodeRequest.finality)

    async def get_operation_result(
        self,
        operation_id: str,
        operation: str,
        max_retries: int,
        frequency: int,
    ) -> Dict[str, Any]:
        response = {"status": OperationStatuses.PENDING.value}

        retries = 0

        while True:
            if retries > max_retries:
                response["data"] = {
                    "errorType": "DKG_CLIENT_ERROR",
                    "errorMessage": "Unable to get results. Max number of retries reached.",
                }
                break

            if retries > 0:
                await asyncio.sleep(frequency)

            retries += 1

            try:
                result = await self._get_operation_result(
                    operation=operation,
                    operation_id=operation_id,
                )
                response = {"data": result}
            except Exception:
                response = {"data": {"status": "NETWORK ERROR"}}

            # Check completion conditions
            if (
                response["data"].get("status") == OperationStatuses.COMPLETED.value
                or response["data"].get("status") == OperationStatuses.FAILED.value
            ):
                break

        return response["data"]

    async def finality_status(
        self,
        ual: UAL,
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

            # Sleep between attempts (except for first try)
            if retries > 0:
                await asyncio.sleep(frequency)

            retries += 1

            try:
                response = await self._finality_status(ual)
                finality = response.get("finality", 0)
            except Exception:
                finality = 0

        return finality

    async def finality(
        self,
        ual: UAL,
        required_confirmations: int,
        max_number_of_retries: int,
        frequency: int,
    ):
        finality_id = 0
        retries = 0

        while finality_id < required_confirmations and retries < max_number_of_retries:
            if retries > max_number_of_retries:
                raise Exception(
                    f"Unable to achieve required confirmations. "
                    f"Max number of retries ({max_number_of_retries}) reached."
                )

            if retries > 0:
                await asyncio.sleep(frequency)

            retries += 1

            try:
                try:
                    response = await self._finality(
                        ual=ual, minimumNumberOfNodeReplications=required_confirmations
                    )
                except Exception as e:
                    response = None
                    print(f"failed: {e}")

                if response is not None:
                    operation_id = response.json().get("operationId", 0)
                    if operation_id >= required_confirmations:
                        finality_id = operation_id

            except Exception as e:
                finality_id = 0
                print(f"Retry {retries + 1}/{max_number_of_retries} failed: {e}")

            return finality_id
