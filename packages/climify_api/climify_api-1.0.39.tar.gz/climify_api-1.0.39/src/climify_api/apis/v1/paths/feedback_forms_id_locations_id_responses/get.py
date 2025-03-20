from dataclasses import dataclass
import typing_extensions
import pytz
import urllib3
from urllib3._collections import HTTPHeaderDict

from climify_api import api_client, exceptions
from datetime import date, datetime, timedelta  # noqa: F401
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
from climify_api.models import FormQuestionType

PATH = 'feedback/forms/{form_id}/locations/{form_id}/responses'

class GetFormResponsesFromLocationById(PathBase):
    def get_form_responses_from_location_by_id(
        self,
        form_id: int,
        location_id: int,
        from_datetime: datetime = None,
        to_datetime: datetime = None,
        access_token: str = None,
        stream: bool = False,
        timeout: typing.Optional[typing.Union[int, typing.Tuple]] = None,
        skip_deserialization: bool = False,
    ) -> ClimifyApiResponse[List[FormQuestionType]]:
        """Returns a list of questions on the given form, along with the responses
        to the form originating from the provided location.

        :param form_id: Form identifier
        :type form_id: int
        :param location_id: Location identifier
        :type location_id: int

        :param access_token: Access token to use for the request
        :type access_token: str, optional
        :param stream: Toggles streaming, defaults to False
        :type stream: bool, optional
        :param timeout: How long to wait for a request in seconds, defaults to None
        :type timeout: typing.Optional[typing.Union[int, typing.Tuple]], optional
        :param skip_deserialization: Toggles whether or not to skip deserialize of the byte response, defaults to False
        :type skip_deserialization: bool, optional

        :raises ApiValueError: Will be raised if invalid inputs are provided
        :raises ClimifyApiException: Will be raised if an error occurred while calling the API
        
        :return: A response with a body containing a list of the from questions including
                 responses.
        :rtype: ClimifyApiResponse[List[FromQuestionDto]]
        """
        # Validate input
        if form_id is None:
            raise ApiValueError("Form id was given as None. A valid form id must be provided.")
        if location_id is None:
            raise ApiValueError("Location id was given as None. A valid location id must be provided.")

        if from_datetime.tzinfo != pytz.UTC:
            from_datetime = from_datetime.astimezone(pytz.UTC)
        
        if to_datetime.tzinfo != pytz.UTC:
            to_datetime = to_datetime.astimezone(pytz.UTC)
            
        # Make rest request
        used_path = PATH.replace('{form_id}',str(form_id))
        used_path = used_path.replace('{location_id}',str(location_id))
        
        query_parameters = []
        for name, value in (
            ('dateTimeFrom', from_datetime.replace(tzinfo=None).isoformat()+'Z' if from_datetime else None), # Sets timezone to None, to remove +HH:MM
            ('dateTimeTo', to_datetime.replace(tzinfo=None).isoformat()+'Z' if to_datetime else None)
        ):
            if value:
                query_parameters.append(f"{name}={value}")
        
        if len(query_parameters) > 0:
            used_path += "?" + "&".join(query_parameters)

        response = self.api_client.call_api(
            resource_path=used_path,
            method='GET',
            access_token=access_token,
            stream=stream,
            timeout=timeout
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
            deserialized_body = TypeAdapter(List[FormQuestionType]).validate_json(response.data) if response.data\
                                else []
            api_response = ClimifyApiResponse[List[FormQuestionType]](
                response=response,
                status=response.status,
                body=deserialized_body,
                headers=response.headers
            )

        return api_response