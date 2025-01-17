from dkg.managers.manager import DefaultRequestManager
from dkg.method import Method
from dkg.modules.module import Module
import time
from dkg.utils.decorators import retry
from dkg.exceptions import (
    OperationNotFinished,
)
from dkg.utils.node_request import (
    NodeRequest,
    validate_operation_status,
)


class NodeService(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _get_operation_result = Method(NodeRequest.get_operation_result)
    _finality_status = Method(NodeRequest.finality_status)
    _finality = Method(NodeRequest.finality)

    def get_operation_result(
        self, operation_id: str, operation: str, max_retries: int, frequency: int
    ):
        @retry(
            catch=OperationNotFinished,
            max_retries=max_retries,
            base_delay=frequency,
            backoff=1,
        )
        def retry_get_operation_result():
            operation_result = self._get_operation_result(
                operation_id=operation_id,
                operation=operation,
            )
            validate_operation_status(operation_result)

            return operation_result

        return retry_get_operation_result()

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

            if retries > 0:
                time.sleep(frequency)

            retries += 1

            try:
                try:
                    response = self._finality_status(ual=ual)
                except Exception as e:
                    response = None
                    print(f"failed: {e}")

                if response is not None:
                    finality = response.get("finality", 0)
                    if finality >= required_confirmations:
                        break

            except Exception:
                finality = 0

        return finality

    def finality(self, ual, required_confirmations, max_number_of_retries, frequency):
        finality_id = 0
        retries = 0

        while finality_id < required_confirmations and retries < max_number_of_retries:
            if retries > max_number_of_retries:
                raise Exception(
                    f"Unable to achieve required confirmations. "
                    f"Max number of retries ({max_number_of_retries}) reached."
                )

            if retries > 0:
                time.sleep(frequency)

            retries += 1

            try:
                try:
                    response = self._finality(
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
