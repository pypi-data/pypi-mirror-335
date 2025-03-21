# Copyright Contributors to the Packit project.
# SPDX-License-Identifier: MIT


import datetime
import json
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import httpx

from requre.cassette import Cassette
from requre.objects import ObjectStorage
from requre.record_and_replace import make_generic, recording, replace


class HTTPXRequestResponseHandling(ObjectStorage):
    __response_keys = ["status_code", "encoding"]
    __ignored = ["cookies"]
    __response_keys_special = ["next_request", "headers", "_elapsed", "_content"]
    __store_indicator = "__store_indicator"
    __implicit_encoding = "utf-8"

    def __init__(
        self,
        store_keys: list,
        cassette: Optional[Cassette] = None,
        response_headers_to_drop=None,
    ) -> None:
        # replace request if given as key and use prettier url
        for index, key in enumerate(store_keys):
            if isinstance(key, httpx.Request):
                store_keys[index] = str(key.url)
                store_keys.insert(index, key.method)
        super().__init__(store_keys, cassette=cassette)
        self.response_headers_to_drop = response_headers_to_drop or []

    def write(
        self, response: httpx.Response, metadata: Optional[Dict] = None
    ) -> httpx.Response:
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

    def to_serializable(self, response: httpx.Response) -> Any:
        output = dict()
        for key in self.__response_keys:
            output[key] = getattr(response, key)
        for key in self.__response_keys_special:
            if key == "headers":
                headers_dict = dict(response.headers)
                for header in self.response_headers_to_drop:
                    if header in headers_dict:
                        headers_dict[header] = None
                output[key] = headers_dict
            if key == "_elapsed":
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
            if key == "next_request":
                output[key] = None
                if getattr(response, "next_request") is not None:
                    output[key] = self.store_keys
        return output

    def from_serializable(self, data: Any) -> httpx.Response:
        # Process the content
        encoding = data["encoding"] or self.__implicit_encoding

        indicator = data[self.__store_indicator]
        content, text, deserialized_json = None, None, None
        if indicator == 0:
            content = data["_content"]  # raw data
        elif indicator == 1:
            text = data["_content"]  # encoded text
        elif indicator == 2:
            deserialized_json = data["_content"]  # JSON
        else:
            raise TypeError("Invalid type of encoded content.")

        response = httpx.Response(
            status_code=data["status_code"],
            headers=data["headers"],
            content=content,
            text=text,
            json=deserialized_json,
        )
        response.encoding = encoding
        response.elapsed = datetime.timedelta(seconds=data.get("elapsed", 0))
        response.next_request = data.get("next_request")

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
def record_httpx(
    _func=None,
    response_headers_to_drop: Optional[List[str]] = None,
    cassette: Optional[Cassette] = None,
):
    """
    Decorator which can be used to store all httpx requests to a file
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
        what="httpx._client.Client.send",
        cassette=cassette,
        decorate=HTTPXRequestResponseHandling.decorator(
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
def recording_httpx(
    response_headers_to_drop: Optional[List[str]] = None, storage_file=None
):
    """
    Context manager which can be used to store all httpx requests to a file
    and replay responses on the next run.

    - The matching is based on `url`.
    - Removes tokens from the url when saving if needed.

    :param _func: can be used to decorate function (with, or without parenthesis).
    :param response_headers_to_drop: list of header names we don't want to save with response
                                        (Will be replaced to `None`.)
    :param storage_file: file for reading and writing data in storage_object
    """
    with recording(
        what="httpx._client.Client.send",
        decorate=HTTPXRequestResponseHandling.decorator(
            item_list=[1],
            response_headers_to_drop=response_headers_to_drop,
        ),
        storage_file=storage_file,
    ) as cassette:
        yield cassette
