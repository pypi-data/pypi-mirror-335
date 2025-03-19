from functools import wraps
from http.client import responses
import json
from logging import getLogger
import requests

from wowool.portal.client.error import ClientError, ServerError

# print("wowool.portal.client.service:", __name__)
logger = getLogger(__name__)

API_PREFIX = "/nlp/v1"


def catch_network_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError as nex:
            raise ClientError(f"Could not reach Portal, {nex}")

    return wrapper


class Service:
    def __init__(
        self,
        url: str,
        headers: dict | None = None,
        auth: tuple[str, str] | None = None,
        **kwargs,
    ):
        self.url = url
        self.headers = headers
        self.auth = auth

    def url_for(self, url):
        return f"{self.url}/{url}"

    def check_response(
        self,
        response_json,
        response_status_code: int,
        expected_status_code: int,
    ):
        if expected_status_code == response_status_code:
            return
        message = (
            response_json["error"]["message"]
            if "error" in response_json and "message" in response_json["error"]
            else f"Portal API call failed: expected status code {expected_status_code}, received {response_status_code} instead"
        )
        type = response_json["type"] if "type" in response_json else None
        details = response_json["details"] if "details" in response_json else None
        raise ServerError(
            message=message,
            status_code=response_status_code,
            type=type,
            details=details,
        )

    @catch_network_errors
    def get(self, url: str, status_code: int, **kwargs):
        logger.debug(f"Request: GET {url}")
        response = requests.get(self.url_for(url), headers=self.headers, auth=self.auth, **kwargs)
        return self._response(response, status_code)

    @catch_network_errors
    def post(self, url: str, status_code: int, data: dict, **kwargs):
        logger.debug(f"Request: POST {url}")
        response = requests.post(self.url_for(url), json=data, headers=self.headers, auth=self.auth, **kwargs)
        return self._response(response, status_code)

    def _response(self, response, status_code):
        try:
            obj = response.json()
        except json.decoder.JSONDecodeError:
            logger.debug(f"No JSON was returned: {response.status_code} - {responses[response.status_code]}")
            raise ServerError(
                message=responses[response.status_code],
                status_code=response.status_code,
            )

        self.check_response(obj, response.status_code, status_code)
        return obj
