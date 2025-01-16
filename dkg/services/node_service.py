from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.constants import OperationStatuses
from dkg.utils.node_request import NodeRequest
from dkg.module import Module
from typing import Dict, Any
import asyncio


class NodeService(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _get_operation_result = Method(NodeRequest.get_operation_result)
    _finality_status = Method(NodeRequest.finality_status)

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
