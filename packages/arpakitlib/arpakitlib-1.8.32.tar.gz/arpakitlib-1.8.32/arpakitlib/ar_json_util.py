# arpakit

import json
from typing import Any

import orjson

from arpakitlib.ar_datetime_util import now_utc_dt

_ARPAKIT_LIB_MODULE_VERSION = "3.0"


def transfer_json_str_to_data(
        json_str: str, fast: bool = False
) -> dict[Any, Any] | list[Any] | None:
    if not isinstance(json_str, str):
        raise ValueError("not isinstance(json_str, str)")
    if fast:
        return orjson.loads(json_str)
    else:
        return json.loads(json_str)


def transfer_data_to_json_str(
        data: dict[Any, Any] | list[Any] | None, beautify: bool = True, fast: bool = False
) -> str:
    if not isinstance(data, dict) and not isinstance(data, list) and data is not None:
        raise ValueError("not isinstance(data, dict) and not isinstance(data, list) and data is not None")
    if fast:
        return orjson.dumps(data).decode()
    else:
        if beautify:
            return json.dumps(data, ensure_ascii=False, indent=2, default=str)
        else:
            return json.dumps(data, ensure_ascii=False, default=str)


def transfer_data_to_json_str_to_data(
        data: dict[Any, Any] | list[Any] | None, fast: bool = False
) -> dict[Any, Any] | list[Any] | None:
    return transfer_json_str_to_data(transfer_data_to_json_str(data=data, fast=fast), fast=fast)


def transfer_json_str_to_data_to_json_str(
        json_str: str, beautify: bool = True, fast: bool = False
) -> str:
    return transfer_data_to_json_str(
        transfer_json_str_to_data(json_str=json_str, fast=fast), beautify=beautify, fast=fast
    )


def __example():
    res = {str(k): v * "123" for k, v in enumerate(list(range(90000)))}

    print("---")

    now = now_utc_dt()
    transfer_data_to_json_str(data=res, beautify=True, fast=False)
    print(now_utc_dt() - now)

    now = now_utc_dt()
    transfer_data_to_json_str(data=res, fast=True)
    print(now_utc_dt() - now)


if __name__ == '__main__':
    __example()
