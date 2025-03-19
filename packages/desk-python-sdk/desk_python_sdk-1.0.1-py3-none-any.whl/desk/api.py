import json
import logging
from typing import Any
import requests as r
from desk.constant.common import BASE_URLS, CRM_URLS
from desk.types import NetworkOption
from desk.utils.error import ClientError, ServerError


class Api:
    def __init__(self, network: NetworkOption, headers: dict = None):
        self.api_url = BASE_URLS[network]
        self.crm_url = CRM_URLS[network]
        self.session = r.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self._logger = logging.getLogger(__name__)

        if headers:
            self.session.headers.update(headers)

    def post(self, url_path: str, payload: Any = None) -> Any:
        payload = payload or {}
        url = self.api_url + url_path
        response = self.session.post(url, json=payload)
        self.__handle_exception(response)

        try:
            return response.json()["data"]
        except ValueError:
            return {"error": f"Could not parse JSON: {response.text}"}
        
    def get(self, url_path: str, params: dict = None):
        url = self.api_url + url_path
        response = self.session.get(url, params=params)
        self.__handle_exception(response)

        try:
            return response.json()["data"]
        except ValueError:
            return {"error": f"Could not parse JSON: {response.text}"}
        
    def __handle_exception(self, response: r.Response):
        status_code = response.status_code
        if status_code < 400:
            return
        if 400 <= status_code < 500:
            try:
                err = json.loads(response.text)
            except json.JSONDecodeError:
                raise Exception(response.text)
            if err is None or err.get("errors") is None or err.get("code") is None or err.get("message") is None:
                raise Exception(f"status_code: {status_code}, response: {response.text}")
            error_data = err.get("errors")
            raise ClientError(status_code, err["code"], err["message"], response.headers, error_data)
        raise ServerError(status_code, response.text)


    def post_crm(self, url_path: str, payload: Any = None) -> Any:
        payload = payload or {}
        url = self.crm_url + url_path
        response = self.session.post(url, json=payload)
        self.__handle_exception(response)

        try:
            return response.json()["data"]
        except ValueError:
            return {"error": f"Could not parse JSON: {response.text}"}
