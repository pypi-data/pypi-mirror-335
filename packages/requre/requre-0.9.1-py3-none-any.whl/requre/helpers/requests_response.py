# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT


import datetime
import json
from contextlib import contextmanager
from io import BytesIO, IOBase
from typing import Any, Dict, Generator, List, Optional
from urllib.parse import urlparse

from requests.models import PreparedRequest, Request, Response
from requests.structures import CaseInsensitiveDict

from requre.cassette import Cassette
from requre.objects import ObjectStorage
from requre.record_and_replace import make_generic, recording, replace


def remove_password_from_url(url):
    urlobject = urlparse(url)
    if urlobject.password:
        return urlobject._replace(
            netloc="{}:{}@{}".format(urlobject.username, "???", urlobject.hostname)
        ).geturl()
    else:
        return url


class FakeBaseHTTPResponse(IOBase):
    def __init__(self, raw_data: bytes, decoded_data: bytes) -> None:
        self.raw_stream = BytesIO(raw_data)
        self.decoded_stream = BytesIO(decoded_data)

    def readable(self) -> bool:
        return True

    def read(
        self,
        amt: Optional[int] = None,
        decode_content: Optional[bool] = None,
        cache_content: bool = False,
    ) -> bytes:
        stream = self.decoded_stream if decode_content else self.raw_stream
        return stream.read(amt)

    def read1(
        self, amt: Optional[int] = None, decode_content: Optional[bool] = None
    ) -> bytes:
        stream = self.decoded_stream if decode_content else self.raw_stream
        return stream.read1(amt)

    def stream(
        self, amt: Optional[int] = 2**16, decode_content: Optional[bool] = None
    ) -> Generator[bytes, None, None]:
        stream = self.decoded_stream if decode_content else self.raw_stream

        def generate():
            while True:
                chunk = stream.read(amt)
                if not chunk:
                    break
                yield chunk

        return generate()

    def _decode(self, data: bytes, decode_content: bool, flush_decoder: bool) -> bytes:
        if not decode_content:
            return data
        return self.decoded_stream.read()


class RequestResponseHandling(ObjectStorage):
    __response_keys = ["status_code", "encoding", "reason"]
    __ignored = ["cookies"]
    __response_keys_special = ["raw", "_next", "headers", "elapsed", "_content"]
    __store_indicator = "__store_indicator"
    __implicit_encoding = "UTF-8"

    def __init__(
        self,
        store_keys: list,
        cassette: Optional[Cassette] = None,
        response_headers_to_drop=None,
    ) -> None:
        # replace request if given as key and use prettier url
        for index, key in enumerate(store_keys):
            if isinstance(key, (Request, PreparedRequest)):
                store_keys[index] = remove_password_from_url(key.url)
                store_keys.insert(index, key.method)
        super().__init__(store_keys, cassette=cassette)
        self.response_headers_to_drop = response_headers_to_drop or []

    def write(self, response: Response, metadata: Optional[Dict] = None) -> Response:
        super().write(response, metadata)
        # TODO: disabled for now, improve next handling if we find it makes sense
        # if getattr(response, "next"):
        #    self.write(getattr(response, "next"))
        return response

    def read(self):
        data = super().read()
        # TODO: disabled for now, improve next handling if we find it makes sense
        # if getattr(data, "next"):
        #    data._next = self.read()
        return data

    def to_serializable(self, response: Response) -> Any:
        output = dict()
        for key in self.__response_keys:
            output[key] = getattr(response, key)
        for key in self.__response_keys_special:
            if key == "raw":
                if hasattr(response.raw, "_decode"):
                    # urllib3.response.BaseHTTPResponse
                    raw_data = response.raw.read(decode_content=False)
                    decoded_data = response.raw._decode(
                        raw_data, decode_content=True, flush_decoder=True
                    )
                    output[key] = raw_data
                    output[f"{key}_decoded"] = decoded_data
                    # replay it back to raw
                    response.raw = FakeBaseHTTPResponse(raw_data, decoded_data)
                else:
                    raw_data = response.raw.read()
                    output[key] = raw_data
                    # replay it back to raw
                    response.raw = BytesIO(raw_data)
            if key == "headers":
                headers_dict = dict(response.headers)
                for header in self.response_headers_to_drop:
                    if header in headers_dict:
                        headers_dict[header] = None
                output[key] = headers_dict
            if key == "elapsed":
                output[key] = response.elapsed.total_seconds()
            if key == "_content":
                what_store = response._content  # type: ignore
                encoding = response.encoding or self.__implicit_encoding
                try:
                    what_store = what_store.decode(encoding)  # type: ignore
                    try:
                        what_store = json.loads(what_store)
                        indicator = 2
                    except json.decoder.JSONDecodeError:
                        indicator = 1
                except (ValueError, AttributeError):
                    indicator = 0
                output[key] = what_store
                output[self.__store_indicator] = indicator
            if key == "_next":
                output[key] = None
                if getattr(response, "next") is not None:
                    output[key] = self.store_keys
        return output

    def from_serializable(self, data: Any) -> Response:
        response = Response()
        for key in self.__response_keys:
            setattr(response, key, data[key])
        for key in self.__response_keys_special:
            if key == "raw":
                if f"{key}_decoded" in data:
                    response.raw = FakeBaseHTTPResponse(
                        data[key], data[f"{key}_decoded"]
                    )
                else:
                    response.raw = BytesIO(data[key])
            if key == "headers":
                response.headers = CaseInsensitiveDict(data[key])
            if key == "elapsed":
                response.elapsed = datetime.timedelta(seconds=data[key])
            if key == "_content":
                encoding = response.encoding or self.__implicit_encoding
                indicator = data[self.__store_indicator]
                if indicator == 0:
                    what_store = data[key]
                elif indicator == 1:
                    what_store = data[key].encode(encoding)
                elif indicator == 2:
                    what_store = json.dumps(data[key])
                    what_store = what_store.encode(encoding)
                response._content = what_store  # type: ignore
            if key == "_next":
                setattr(response, "_next", data[key])
        return response

    @classmethod
    def decorator_all_keys(
        cls,
        storage_object_kwargs=None,
        cassette: Cassette = None,
        response_headers_to_drop=None,
    ) -> Any:
        """
        Class method for what should be used as decorator of import replacing system
        This use all arguments of function as keys

        :param func: Callable object
        :param storage_object_kwargs: forwarded to the storage object
        :param response_headers_to_drop: list of header names we don't want to save with response
                                            (Will be replaced to `None`.)
        :param cassette: Cassette instance to pass inside object to work with
        :return: CassetteExecution class with function and cassette instance
        """
        storage_object_kwargs = storage_object_kwargs or {}
        if response_headers_to_drop:
            storage_object_kwargs["response_headers_to_drop"] = response_headers_to_drop
        return super().decorator_all_keys(
            storage_object_kwargs,
            cassette=cassette,
        )

    @classmethod
    def decorator(
        cls,
        *,
        item_list: list,
        map_function_to_item=None,
        storage_object_kwargs=None,
        cassette: Cassette = None,
        response_headers_to_drop=None,
    ) -> Any:
        """
        Class method for what should be used as decorator of import replacing system
        This use list of selection of *args or **kwargs as arguments of function as keys

        :param item_list: list of values of *args nums,  **kwargs names to use as keys
        :param map_function_to_item: dict of function to apply to keys before storing
                                  (have to be listed in item_list)
        :param storage_object_kwargs: forwarded to the storage object
        :param response_headers_to_drop: list of header names we don't want to save with response
                                        (Will be replaced to `None`.)
        :param cassette: Cassette instance to pass inside object to work with
        :return: CassetteExecution class with function and cassette instance
        """
        storage_object_kwargs = storage_object_kwargs or {}
        if response_headers_to_drop:
            storage_object_kwargs["response_headers_to_drop"] = response_headers_to_drop
        return super().decorator(
            item_list=item_list,
            map_function_to_item=map_function_to_item,
            storage_object_kwargs=storage_object_kwargs,
            cassette=cassette,
        )

    @classmethod
    def decorator_plain(
        cls,
        storage_object_kwargs=None,
        cassette: Cassette = None,
        response_headers_to_drop=None,
    ) -> Any:
        """
        Class method for what should be used as decorator of import replacing system
        This use no arguments of function as keys

        :param func: Callable object
        :param storage_object_kwargs: forwarded to the storage object
        :param response_headers_to_drop: list of header names we don't want to save with response
                                          (Will be replaced to `None`.)
        :param cassette: Cassette instance to pass inside object to work with
        :return: CassetteExecution class with function and cassette instance
        """
        storage_object_kwargs = storage_object_kwargs or {}
        if response_headers_to_drop:
            storage_object_kwargs["response_headers_to_drop"] = response_headers_to_drop
        return super().decorator_plain(
            storage_object_kwargs=storage_object_kwargs,
            cassette=cassette,
        )


@make_generic
def record_requests(
    _func=None,
    response_headers_to_drop: Optional[List[str]] = None,
    cassette: Optional[Cassette] = None,
):
    """
    Decorator which can be used to store all requests to a file
    and replay responses on the next run.

    - The matching is based on `url`.
    - Removes tokens from the url when saving if needed.

    Can be used with or without parenthesis.

    :param _func: can be used to decorate function (with, or without parenthesis).
    :param response_headers_to_drop: list of header names we don't want to save with response
                                        (Will be replaced to `None`.)
    :param storage_file: str - storage file to be passed to cassette instance if given,
                               else it creates new instance
    :param cassette: Cassette instance to pass inside object to work with
    """

    response_headers_to_drop = response_headers_to_drop or []
    replace_decorator = replace(
        what="requests.sessions.Session.send",
        cassette=cassette,
        decorate=RequestResponseHandling.decorator(
            item_list=[1],
            response_headers_to_drop=response_headers_to_drop,
            cassette=cassette,
        ),
    )

    if _func is not None:
        return replace_decorator(_func)
    else:
        return replace_decorator


@contextmanager
def recording_requests(
    response_headers_to_drop: Optional[List[str]] = None, storage_file=None
):
    """
    Context manager which can be used to store all requests to a file
    and replay responses on the next run.

    - The matching is based on `url`.
    - Removes tokens from the url when saving if needed.

    :param _func: can be used to decorate function (with, or without parenthesis).
    :param response_headers_to_drop: list of header names we don't want to save with response
                                        (Will be replaced to `None`.)
    :param storage_file: file for reading and writing data in storage_object
    """
    with recording(
        what="requests.sessions.Session.send",
        decorate=RequestResponseHandling.decorator(
            item_list=[1],
            response_headers_to_drop=response_headers_to_drop,
        ),
        storage_file=storage_file,
    ) as cassette:
        yield cassette
