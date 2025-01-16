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

            retries += 1
            await asyncio.sleep(frequency)

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
                or response["data"].get("data", {}).get("minAcksReached")
            ):
                break

        return response["data"]
