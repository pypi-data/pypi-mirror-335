import json
from typing import Dict, Optional
from scrapy.http import Request, JsonRequest, FormRequest
from rnet import Proxy, Method
from urllib.parse import parse_qs



class RnetOptionsParser:

    def __init__(self, request: Request):
        self._request = request

    def as_dict(self) -> Dict:
        return {
            "impersonate": self._request.meta.get("impersonate"),
            "impersonate_os": self._request.meta.get("impersonate_os"),
        }
    

class RequestParser:

    def __init__(self, request: Request):
        self._request = request

    @property
    def url(self) -> str:
        return self._request.url

    @property
    def method(self) -> Optional[Method]:
        _mapping = {
            "GET": Method.GET,
            "POST": Method.POST,
            "HEAD": Method.HEAD,
            "OPTIONS": Method.OPTIONS,
        }
        return _mapping[self._request.method]

    @property
    def headers(self) -> Dict:
        headers = self._request.headers.to_unicode_dict()
        return dict(headers)

    @property
    def proxy(self) -> Optional[Proxy]:
        _proxy = self._request.meta.get("proxy")
        if _proxy:
            return Proxy.all(_proxy)
    
    @property
    def cookies(self) -> Optional[Dict[str, str]]:
        cookies = self._request.cookies
        if isinstance(cookies, list):
            return {k: v for cookie in cookies for k, v in cookie.items()}
        elif isinstance(cookies, dict):
            return {k: v for k, v in cookies.items()}
        else:
            return {}
    
    @property
    def allow_redirects(self) -> bool:
        return False if self._request.meta.get("dont_redirect") else True
    
    @staticmethod
    def bytes_to_dict(form_bytes: bytes) -> Dict:
        if form_bytes == b"":
            return {}
        form_dict = parse_qs(form_bytes.decode())
        form_dict_single = {k: v[0] for k, v in form_dict.items()}
        return form_dict_single
    
    def as_dict(self) -> Dict:
        body = self._request.body
        payload =  {}
        if body != b"":
            if isinstance(self._request, FormRequest):
                payload = {
                    "form": [
                        (k, v)
                        for k, v in self.bytes_to_dict(body).items()
                    ]
                }
            elif isinstance(self._request, JsonRequest):
                payload = {
                    "json": json.loads(body.decode("utf-8"))
                }
            elif isinstance(self._request, Request):
                payload = {
                    "body": body
                }
        request_args = {}
        # property is different than attribute here e.g ('impersonate', <property object at 0x753f96955350>) ('__dict__', <attribute '__dict__' of 'RequestParser' objects>)
        for property_name, obj in self.__class__.__dict__.items():
            if isinstance(obj, property):
                property_value = getattr(self, property_name)
                if property_value is not None:
                    request_args[property_name] = property_value
        request_args.update(payload)
        return request_args

