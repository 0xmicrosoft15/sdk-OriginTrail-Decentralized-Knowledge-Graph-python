from dkg.constants import DefaultParameters, ZERO_ADDRESS


class InputService:
    def __init__(self, manager):
        self.manager = manager

    def get_asset_get_arguments(self, options):
        return {
            # "blockchain": self.get_blockchain(options),
            "endpoint": self.get_endpoint(options),
            "port": self.get_port(options),
            "max_number_of_retries": self.get_max_number_of_retries(options),
            "frequency": self.get_frequency(options),
            "state": self.get_state(options),
            "include_metadata": self.get_include_metadata(options),
            "content_type": self.get_content_type(options),
            "validate": self.get_validate(options),
            "output_format": self.get_output_format(options),
            "auth_token": self.get_auth_token(options),
            "hash_function_id": self.get_hash_function_id(options),
            "paranet_ual": self.get_paranet_ual(options),
            "subject_ual": self.get_subject_ual(options),
        }

    def get_asset_create_arguments(self, options):
        return {
            # "blockchain": self.get_blockchain(options),
            "endpoint": self.get_endpoint(options),
            "port": self.get_port(options),
            "max_number_of_retries": self.get_max_number_of_retries(options),
            "frequency": self.get_frequency(options),
            "epochs_num": self.get_epochs_num(options),
            "hash_function_id": self.get_hash_function_id(options),
            "score_function_id": self.get_score_function_id(options),
            "immutable": self.get_immutable(options),
            "token_amount": self.get_token_amount(options),
            "auth_token": self.get_auth_token(options),
            "payer": self.get_payer(options),
            "minimum_number_of_finalization_confirmations": self.get_minimum_number_of_finalization_confirmations(
                options
            )
            or 3,
            "minimum_number_of_node_replications": self.get_minimum_number_of_node_replications(
                options
            ),
        }

    def get_query_arguments(self, options):
        return {
            "graph_location": self.get_graph_location(options),
            "graph_state": self.get_graph_state(options),
            "endpoint": self.get_endpoint(options),
            "port": self.get_port(options),
            "max_number_of_retries": self.get_max_number_of_retries(options),
            "frequency": self.get_frequency(options),
            "auth_token": self.get_auth_token(options),
            "paranet_ual": self.get_paranet_ual(options),
            "repository": self.get_repository(options),
        }

    def get_endpoint(self, options):
        return (
            options.get("endpoint") or self.manager.node_provider.endpoint_uri or None
        )

    # def get_blockchain(self, options):
    #     return (
    #         options.get("blockchain")
    #         or self.manager.blockchain_provider.blockchain
    #         or None
    #     )

    def get_port(self, options):
        return options.get("port") or DefaultParameters.PORT.value

    def get_max_number_of_retries(self, options):
        return (
            options.get("max_number_of_retries")
            or DefaultParameters.MAX_NUMBER_OF_RETRIES.value
        )

    def get_frequency(self, options):
        return options.get("frequency") or DefaultParameters.FREQUENCY.value

    def get_state(self, options):
        return options.get("state") or DefaultParameters.STATE.value

    def get_include_metadata(self, options):
        return (
            options.get("include_metadata") or DefaultParameters.INCLUDE_METADATA.value
        )

    def get_content_type(self, options):
        return options.get("content_type") or DefaultParameters.CONTENT_TYPE.value

    def get_validate(self, options):
        return options.get("validate") or DefaultParameters.VALIDATE.value

    def get_output_format(self, options):
        return options.get("output_format") or DefaultParameters.OUTPUT_FORMAT.value

    def get_auth_token(self, options):
        return options.get("auth_token") or self.manager.node_provider.auth_token

    def get_hash_function_id(self, options):
        return (
            options.get("hash_function_id") or DefaultParameters.HASH_FUNCTION_ID.value
        )

    def get_paranet_ual(self, options):
        return options.get("paranet_ual") or DefaultParameters.PARANET_UAL.value

    def get_subject_ual(self, options):
        return options.get("subject_ual") or DefaultParameters.GET_SUBJECT_UAL.value

    def get_epochs_num(self, options):
        return options.get("epochs_num") or None

    def get_immutable(self, options):
        return options.get("immutable") or DefaultParameters.IMMUTABLE.value

    def get_token_amount(self, options):
        return options.get("token_amount") or None

    def get_payer(self, options):
        return options.get("payer") or ZERO_ADDRESS

    def get_minimum_number_of_finalization_confirmations(self, options):
        return options.get("minimum_number_of_finalization_confirmations") or None

    def get_minimum_number_of_node_replications(self, options):
        return options.get("minimum_number_of_node_replications") or None

    def get_score_function_id(self, options):
        enviroment = (
            options.get("environment")
            or self.manager.blockchain_provider.environment
            or DefaultParameters.ENVIRONMENT.value
        )
        blockchain_name = (
            options.get("immutable") or self.manager.blockchain_provider.blockchain_id
        )

        return (
            DEFAULT_PROXIMITY_SCORE_FUNCTIONS_PAIR_IDS[
                self.manager.blockchain_provider.environment
            ][blockchain_id],
        )

    def get_graph_location(self, options):
        return (
            options.get("graph_location")
            or options.get("paranet_ual")
            or DefaultParameters.GRAPH_LOCATION.value
        )

    def get_graph_state(self, options):
        return options.get("graph_state") or DefaultParameters.GRAPH_STATE.value

    def get_repository(self, options):
        return options.get("repository") or None
