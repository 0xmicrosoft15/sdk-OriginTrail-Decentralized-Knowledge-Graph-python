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

from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.module import Module
from dkg.types import NQuads
from dkg.utils.node_request import NodeRequest
from dkg.constants import Operations
from dkg.services.input_service import InputService
from dkg.services.node_service import NodeService


class Graph(Module):
    def __init__(
        self,
        manager: DefaultRequestManager,
        input_service: InputService,
        node_service: NodeService,
    ):
        self.manager = manager
        self.input_service = input_service
        self.node_service = node_service

    _query = Method(NodeRequest.query)

    async def query(
        self,
        query: str,
        options: dict = {},
    ) -> NQuads:
        arguments = self.input_service.get_query_arguments(options)

        max_number_of_retries = arguments.get("max_number_of_retries")
        frequency = arguments.get("frequency")
        paranet_ual = arguments.get("paranet_ual")
        repository = arguments.get("repository")

        parsed_query = parseQuery(query)
        query_type = parsed_query[1].name.replace("Query", "").upper()

        result = await self._query(query, query_type, repository, paranet_ual)
        operation_id = result.get("operationId")
        operation_result = await self.node_service.get_operation_result(
            operation_id, Operations.QUERY.value, max_number_of_retries, frequency
        )

        return operation_result["data"]
