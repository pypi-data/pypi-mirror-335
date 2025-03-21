import math
from typing import Dict, Union
from .currency_error import CurrencyError
from .currency_interface import currency_interface


def round_value(n: float, d: int = 2) -> float:
    factor = 10**d
    return round(n * factor) / factor


def to_scrap(value: float) -> float:
    metal = math.floor(value)
    scrap_in_metal = round_value(value - metal)
    scrap = metal * 9 + (scrap_in_metal * 100) / 11
    return round(scrap * 2) / 2


def to_refined(value: float) -> float:
    is_negative = value < 0
    metal = (-1 if is_negative else 1) * math.floor(abs(value) / 9)
    remaining_metal = value - metal * 9

    rounding = (
        math.floor
        if (
            (is_negative and remaining_metal < -5)
            or (not is_negative and remaining_metal < 5)
        )
        else math.ceil
    )

    scrap = rounding(remaining_metal * 11) / 100
    return round_value(metal + scrap)


def fix_metal(metal: float) -> float:
    return to_refined(to_scrap(metal))


def fix_currency(currency: Dict[str, float]) -> Dict[str, float]:
    return {
        "keys": currency.get("keys", 0),
        "metal": fix_metal(currency.get("metal", 0)),
    }


def from_keys_to_currency(value: float, conversion: float = 0) -> Dict[str, float]:
    is_negative = value < 0
    keys = math.ceil(value) if is_negative else math.floor(value)
    metal_in_keys = round_value(value - keys)

    if metal_in_keys and not conversion:
        raise CurrencyError("Conversion value is required when metal is present.")

    conversion_in_scrap = to_scrap(conversion)
    scrap = round(metal_in_keys * conversion_in_scrap)
    metal = to_refined(scrap)

    return {"keys": keys, "metal": metal}


def is_equal(
    currency_a: Union[currency_interface, Dict[str, float]],
    currency_b: Union[currency_interface, Dict[str, float]],
) -> bool:
    # Handle both currency_interface and dict types
    keys_a = (
        currency_a.keys if hasattr(currency_a, "keys") else currency_a.get("keys", 0)
    )
    metal_a = (
        currency_a.metal if hasattr(currency_a, "metal") else currency_a.get("metal", 0)
    )
    keys_b = (
        currency_b.keys if hasattr(currency_b, "keys") else currency_b.get("keys", 0)
    )
    metal_b = (
        currency_b.metal if hasattr(currency_b, "metal") else currency_b.get("metal", 0)
    )

    return keys_a == keys_b and metal_a == metal_b


def is_bigger(
    currency_a: Union[currency_interface, Dict[str, float]],
    currency_b: Union[currency_interface, Dict[str, float]],
) -> bool:
    # Handle both currency_interface and dict types
    keys_a = (
        currency_a.keys if hasattr(currency_a, "keys") else currency_a.get("keys", 0)
    )
    metal_a = (
        currency_a.metal if hasattr(currency_a, "metal") else currency_a.get("metal", 0)
    )
    keys_b = (
        currency_b.keys if hasattr(currency_b, "keys") else currency_b.get("keys", 0)
    )
    metal_b = (
        currency_b.metal if hasattr(currency_b, "metal") else currency_b.get("metal", 0)
    )

    return keys_a > keys_b or (keys_a == keys_b and metal_a > metal_b)


def is_smaller(
    currency_a: Union[currency_interface, Dict[str, float]],
    currency_b: Union[currency_interface, Dict[str, float]],
) -> bool:
    # Handle both currency_interface and dict types
    keys_a = (
        currency_a.keys if hasattr(currency_a, "keys") else currency_a.get("keys", 0)
    )
    metal_a = (
        currency_a.metal if hasattr(currency_a, "metal") else currency_a.get("metal", 0)
    )
    keys_b = (
        currency_b.keys if hasattr(currency_b, "keys") else currency_b.get("keys", 0)
    )
    metal_b = (
        currency_b.metal if hasattr(currency_b, "metal") else currency_b.get("metal", 0)
    )

    return keys_a < keys_b or (keys_a == keys_b and metal_a < metal_b)


def is_bigger_or_equal(
    currency_a: Union[currency_interface, Dict[str, float]],
    currency_b: Union[currency_interface, Dict[str, float]],
) -> bool:
    # Handle both currency_interface and dict types
    keys_a = (
        currency_a.keys if hasattr(currency_a, "keys") else currency_a.get("keys", 0)
    )
    metal_a = (
        currency_a.metal if hasattr(currency_a, "metal") else currency_a.get("metal", 0)
    )
    keys_b = (
        currency_b.keys if hasattr(currency_b, "keys") else currency_b.get("keys", 0)
    )
    metal_b = (
        currency_b.metal if hasattr(currency_b, "metal") else currency_b.get("metal", 0)
    )

    return keys_a > keys_b or (keys_a == keys_b and metal_a >= metal_b)


def is_smaller_or_equal(
    currency_a: Union[currency_interface, Dict[str, float]],
    currency_b: Union[currency_interface, Dict[str, float]],
) -> bool:
    # Handle both currency_interface and dict types
    keys_a = (
        currency_a.keys if hasattr(currency_a, "keys") else currency_a.get("keys", 0)
    )
    metal_a = (
        currency_a.metal if hasattr(currency_a, "metal") else currency_a.get("metal", 0)
    )
    keys_b = (
        currency_b.keys if hasattr(currency_b, "keys") else currency_b.get("keys", 0)
    )
    metal_b = (
        currency_b.metal if hasattr(currency_b, "metal") else currency_b.get("metal", 0)
    )

    return keys_a < keys_b or (keys_a == keys_b and metal_a <= metal_b)


def pluralize_keys(value: float) -> str:
    if value == 0:
        return "0 keys"

    if value < 0:
        return f"{value} {'key' if value == -1 else 'keys'}"
    else:
        return f"{value} {'key' if value == 1 else 'keys'}"
