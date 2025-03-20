from dataclasses import dataclass
import typing_extensions
import urllib3
from urllib3._collections import HTTPHeaderDict

from climify_api import api_client, exceptions
from datetime import date, datetime  # noqa: F401
import decimal  # noqa: F401
import functools  # noqa: F401
import io  # noqa: F401
import re  # noqa: F401
import typing  # noqa: F401
import typing_extensions  # noqa: F401
import uuid  # noqa: F401
from typing import List
from pydantic import TypeAdapter


from climify_api.apis.PathBase import PathBase  # noqa: F401

from climify_api.exceptions import ApiValueError, ClimifyApiException
from climify_api.api_client import ClimifyApiResponse, ClimifyApiResponseWithoutDeserialization
from climify_api.models import MeteringPointDto

PATH = 'buildings/{id}/metering-points'

class GetBuildingMeteringPointsById(PathBase):
    # this class is used by api classes that refer to endpoints with operationId fn names

    def get_building_metering_points_by_id(
        self,
        building_id: int,
        access_token: str = None,
        stream: bool = False,
        timeout: typing.Optional[typing.Union[int, typing.Tuple]] = None,
        skip_deserialization: bool = False,
    ) -> ClimifyApiResponse[List[MeteringPointDto]]:
        """Returns the metering points associated with the provided building.

        :param building_id: Building identifier
        :type building_id: int
        :param access_token: Access token to use for the request
        :type access_token: str, optional
        :param stream: Toggles streaming. Defaults to False.
        :type stream: bool, optional
        :param timeout: How long to wait for a request in seconds. Defaults to None.
        :type timeout: typing.Optional[typing.Union[int, typing.Tuple]], optional
        :param skip_deserialization: Toggles whether or not to skip deserialize of the byte response. Defaults to False.
        :type skip_deserialization: bool, optional

        :raises ApiValueError: Will be raised if invalid inputs are provided
        :raises ClimifyApiException: Will be raised if an error occurred while calling the API

        :return: A response with a body containing the list of metering points
        :rtype: ClimifyApiResponse[List[MeteringPointDto]]
        """
        # Validate input
        if building_id is None:
            raise ApiValueError("Building id was given as None. A valid building id must be provided.")

        # Make rest request
        used_path = PATH.replace('{id}',str(building_id))

        response = self.api_client.call_api(
            resource_path=used_path,
            method='GET',
            access_token=access_token,
            stream=stream,
            timeout=timeout,
        )

        if not 200 <= response.status <= 299:
            raise ClimifyApiException(
                status=response.status,
                reason=response.reason,
                api_response=response
            )
        
        if skip_deserialization:
            api_response = ClimifyApiResponseWithoutDeserialization(response=response)
        else:
            # Deserialize response
            deserialized_body = TypeAdapter(List[MeteringPointDto]).validate_json(response.data)
            api_response = ClimifyApiResponse[List[MeteringPointDto]](
                response=response,
                status=response.status,
                body=deserialized_body,
                headers=response.headers
            )


        return api_response