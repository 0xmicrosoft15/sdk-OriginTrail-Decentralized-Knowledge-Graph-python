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


from rdflib.plugins.sparql.parser import parseQuery

from dkg.managers.async_manager import AsyncRequestManager
from dkg.modules.async_module import AsyncModule
from dkg.types import NQuads
from dkg.constants import Status
from dkg.services.input_service import InputService
from dkg.services.node_services.async_node_service import AsyncNodeService
from dkg.types import UAL


class AsyncGraph(AsyncModule):
    def __init__(
        self,
        manager: AsyncRequestManager,
        input_service: InputService,
        node_service: AsyncNodeService,
    ):
        self.manager = manager
        self.input_service = input_service
        self.node_service = node_service

    async def query(
        self,
        query: str,
        options: dict = None,
    ) -> NQuads:
        if options is None:
            options = {}

        arguments = self.input_service.get_query_arguments(options)

        paranet_ual = arguments.get("paranet_ual")
        repository = arguments.get("repository")

        parsed_query = parseQuery(query)
        query_type = parsed_query[1].name.replace("Query", "").upper()

        result = await self.node_service.query(
            query, query_type, repository, paranet_ual
        )
        result.encoding = "utf-8"

        return result.get("data")

    async def publish_finality(self, UAL: UAL, options=None):
        if options is None:
            options = {}

        arguments = self.input_service.get_publish_finality_arguments(options)
        max_number_of_retries = arguments.get("max_number_of_retries")
        minimum_number_of_finalization_confirmations = arguments.get(
            "minimum_number_of_finalization_confirmations"
        )
        frequency = arguments.get("frequency")
        try:
            finality_status_result = await self.node_service.finality_status(
                UAL,
                minimum_number_of_finalization_confirmations,
                max_number_of_retries,
                frequency,
            )
        except Exception as e:
            return {"status": Status.ERROR.value, "error": str(e)}

        if finality_status_result == 0:
            try:
                finality_operation_id = await self.node_service.finality(
                    UAL,
                    minimum_number_of_finalization_confirmations,
                    max_number_of_retries,
                    frequency,
                )
            except Exception as e:
                return {"status": Status.ERROR.value, "error": str(e)}

            try:
                return await self.node_service.get_operation_result(
                    finality_operation_id, "finality", max_number_of_retries, frequency
                )
            except Exception as e:
                return {"status": Status.NOT_FINALIZED.value, "error": str(e)}

        elif finality_status_result >= minimum_number_of_finalization_confirmations:
            return {
                "status": Status.FINALIZED.value,
                "numberOfConfirmations": finality_status_result,
                "requiredConfirmations": minimum_number_of_finalization_confirmations,
            }
        else:
            return {
                "status": Status.NOT_FINALIZED.value,
                "numberOfConfirmations": finality_status_result,
                "requiredConfirmations": minimum_number_of_finalization_confirmations,
            }
