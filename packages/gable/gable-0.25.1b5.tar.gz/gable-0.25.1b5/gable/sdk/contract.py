import json
from typing import Any, List, Tuple, Union

import pydantic
from gable.api.client import GableAPIClient
from gable.openapi import (
    GableSchemaContractField,
    PostContractRequest,
    PostContractResponse,
)
from gable.sdk.converters.trino import (
    convert_trino_timestamp_to_spark_timestamp,
    trino_to_gable_type,
)

from .helpers import external_to_internal_contract_input
from .models import ContractPublishResponse, ExternalContractInput, TrinoDataType


class GableContract:
    def __init__(self, api_endpoint, api_key) -> None:
        self.api_client = GableAPIClient(api_endpoint, api_key)

    def publish(
        self,
        contracts: list[ExternalContractInput],
    ) -> ContractPublishResponse:
        api_response, success, _status_code = self.api_client.post_contract(
            PostContractRequest(
                __root__=[
                    external_to_internal_contract_input(contract)
                    for contract in contracts
                ],
            )
        )

        # Currently, the behavior is either all contracts are published or none are (if there is one invalid contract)
        # Ideally, we can refactor this code and the API to allow for partial success in the future

        if not success or not isinstance(api_response, PostContractResponse):
            failure_message = (
                api_response.message
                if isinstance(api_response, PostContractResponse)
                else "Unknown error"
            )
            return ContractPublishResponse(
                success=False, updatedContractIds=[], message=failure_message
            )
        else:
            updated_contract_ids = api_response.contractIds
            return ContractPublishResponse(
                success=True,
                updatedContractIds=updated_contract_ids,
                message=api_response.message,
            )

    @staticmethod
    def trino_to_gable_schema(
        dict_schema: dict[
            str, Union[str, Union[TrinoDataType, Tuple[TrinoDataType, Tuple[Any, ...]]]]
        ],
        convert_to_spark_types: bool = False,
    ) -> List[GableSchemaContractField]:
        results = [
            trino_to_gable_type(key, value) for key, value in dict_schema.items()
        ]
        if convert_to_spark_types:
            results = [
                convert_trino_timestamp_to_spark_timestamp(result) for result in results
            ]
        return results

    @staticmethod
    def json_schema_to_gable_schema(
        schema: Union[str, dict[str, Any]],
    ) -> List[GableSchemaContractField]:
        import recap
        import recap.types
        from recap.converters.json_schema import JSONSchemaConverter

        # JSONSchemaConverter expects a string, so serialize if it's a dict
        if isinstance(schema, dict):
            schema = json.dumps(schema)
        converter = JSONSchemaConverter()

        return [
            pydantic.parse_obj_as(GableSchemaContractField, recap.types.to_dict(o))
            for o in converter.to_recap(schema).fields
        ]
