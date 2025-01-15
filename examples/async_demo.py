import asyncio
import json
import time
from dkg import DKG
from dkg.constants import Environments, BlockchainIds
from dkg.providers import BlockchainProvider, NodeHTTPProvider


async def main():
    node_provider = NodeHTTPProvider(
        endpoint_uri="https://v6-pegasus-node-01.origin-trail.network:8900",
        api_version="v1",
    )
    blockchain_provider = BlockchainProvider(
        Environments.TESTNET.value,
        BlockchainIds.BASE_TESTNET.value,
    )

    def divider():
        print("==================================================")
        print("==================================================")
        print("==================================================")

    def print_json(json_dict: dict):
        print(json.dumps(json_dict, indent=4))

    content = {
        "public": {
            "@context": "https://schema.org",
            "@id": "https://ford.mustang/2024",
            "@type": "Car",
            "name": "Ford Mustang",
            "brand": {"@type": "Brand", "name": "Ford"},
            "model": "Mustang",
            "manufacturer": {"@type": "Organization", "name": "Ford Motor Company"},
            "fuelType": "Gasoline",
            "numberOfDoors": 2,
            "vehicleEngine": {
                "@type": "EngineSpecification",
                "engineType": "V8",
                "enginePower": {
                    "@type": "QuantitativeValue",
                    "value": "450",
                    "unitCode": "BHP",
                },
            },
            "driveWheelConfiguration": "RWD",
            "speed": {"@type": "QuantitativeValue", "value": "240", "unitCode": "KMH"},
        }
    }

    async with DKG(node_provider, blockchain_provider) as dkg:
        divider()

        info_result = dkg.node.info
        print("======================== NODE INFO RECEIVED")
        print_json(info_result)

        divider()

        # Not async yet
        start_time = time.time()
        create_asset_result = dkg.asset.create(
            content=content,
            options={
                "epochs_num": 2,
                "minimum_number_of_finalization_confirmations": 3,
                "minimum_number_of_node_replications": 1,
                # "token_amount": 100,
            },
        )
        print(
            f"======================== ASSET CREATED in {time.time() - start_time} seconds"
        )
        print_json(create_asset_result)

        divider()

        # start_time = time.time()
        # get_result = dkg.asset.get(create_asset_result.get("UAL"))
        # print(
        #     f"======================== ASSET GET in {time.time() - start_time} seconds"
        # )
        # print_json(get_result)

        # divider()

        # This one is async
        start_time = time.time()
        query_operation_result = await dkg.graph.query(
            """
            PREFIX SCHEMA: <http://schema.org/>
            SELECT ?s ?modelName
            WHERE {
                ?s schema:model ?modelName .
            }
            """
        )
        print(
            f"======================== ASSET QUERY in {time.time() - start_time} seconds"
        )
        print_json(query_operation_result)


if __name__ == "__main__":
    asyncio.run(main())
