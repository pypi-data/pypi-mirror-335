import math
from typing import Dict, Union, Optional
from .currency_error import CurrencyError
from .currency_interface import currency_interface
from .currency_helper import (
    round_value,
    to_scrap,
    to_refined,
    fix_metal,
    from_keys_to_currency,
    is_equal,
    is_bigger,
    is_smaller,
    is_bigger_or_equal,
    is_smaller_or_equal,
    pluralize_keys,
)


class Currency(currency_interface):
    def __init__(self, currency: Dict[str, float] = None):
        if currency is None:
            currency = {}

        self.keys = currency.get("keys", 0)
        self.metal = fix_metal(currency.get("metal", 0))

    @classmethod
    def from_scrap(cls, scrap: float, conversion: float = 0) -> "Currency":
        conversion_in_scrap = to_scrap(conversion)
        rounding = math.ceil if scrap < 0 else math.floor
        keys = rounding(scrap / conversion_in_scrap) if conversion_in_scrap else 0
        metal_in_scrap = scrap - keys * conversion_in_scrap
        metal = to_refined(metal_in_scrap)

        return cls({"keys": keys, "metal": metal})

    @classmethod
    def from_keys(cls, value: float, conversion: float = 0) -> "Currency":
        return cls(from_keys_to_currency(value, conversion))

    def clone(self) -> "Currency":
        return Currency({"keys": self.keys, "metal": self.metal})

    def is_empty(self) -> bool:
        return self.keys == 0 and self.metal == 0

    def to_scrap(self, conversion: float = 0) -> float:
        if self.keys and not conversion:
            raise CurrencyError("Conversion value is required when keys are present.")

        conversion_in_scrap = to_scrap(conversion)
        metal_in_scrap = to_scrap(self.metal)
        keys_in_scrap = self.keys * conversion_in_scrap

        return keys_in_scrap + metal_in_scrap

    def to_keys(self, conversion: float = 0) -> float:
        if self.metal and not conversion:
            raise CurrencyError("Conversion value is required when metal is present.")

        conversion_in_scrap = to_scrap(conversion)
        metal_in_scrap = to_scrap(self.metal)
        metal_in_keys = (
            round_value(metal_in_scrap / conversion_in_scrap) if conversion else 0
        )

        return self.keys + metal_in_keys

    def __str__(self) -> str:
        if not self.keys and not self.metal:
            return "0 keys, 0 metal"

        currency = ""

        if self.keys:
            currency += pluralize_keys(self.keys)

        if self.metal:
            if currency:
                currency += ", "

            currency += f"{self.metal} metal"

        return currency

    def to_dict(self) -> Dict[str, float]:
        return {"keys": self.keys, "metal": self.metal}

    def add_scrap(self, value: float, conversion: float = 0) -> "Currency":
        current_scrap_value = self.to_scrap(conversion)
        total = current_scrap_value + value
        currency = Currency.from_scrap(total, conversion)
        self.keys = currency.keys
        self.metal = currency.metal
        return self

    def add_metal(self, value: float, conversion: Optional[float] = None) -> "Currency":
        return self.add_scrap(to_scrap(value), conversion)

    def add_keys(self, value: float, conversion: float) -> "Currency":
        return self.add_currency(from_keys_to_currency(value, conversion), conversion)

    def add_currency(
        self,
        currency: Union[currency_interface, Dict[str, float]],
        conversion: Optional[float] = None,
    ) -> "Currency":
        return self.add_scrap(Currency(currency).to_scrap(conversion), conversion)

    def remove_scrap(
        self, value: float, conversion: Optional[float] = None
    ) -> "Currency":
        return self.add_scrap(-value, conversion)

    def remove_metal(
        self, value: float, conversion: Optional[float] = None
    ) -> "Currency":
        return self.add_metal(-value, conversion)

    def remove_keys(self, value: float, conversion: float) -> "Currency":
        return self.add_keys(-value, conversion)

    def remove_currency(
        self,
        currency: Union[currency_interface, Dict[str, float]],
        conversion: Optional[float] = None,
    ) -> "Currency":
        # For dictionary input, we need to call get() method
        if isinstance(currency, dict):
            keys = currency.get("keys", 0)
        metal = (
            currency.metal if hasattr(currency, "metal") else currency.get("metal", 0)
        )

        # Create a new currency dict with negated values
        return self.add_currency({"keys": -keys, "metal": -metal}, conversion)

    def is_equal(self, currency: Union[currency_interface, Dict[str, float]]) -> bool:
        return is_equal(self, currency)

    def is_bigger(self, currency: Union[currency_interface, Dict[str, float]]) -> bool:
        return is_bigger(self, currency)

    def is_smaller(self, currency: Union[currency_interface, Dict[str, float]]) -> bool:
        return is_smaller(self, currency)

    def is_bigger_or_equal(
        self, currency: Union[currency_interface, Dict[str, float]]
    ) -> bool:
        return is_bigger_or_equal(self, currency)

    def is_smaller_or_equal(
        self, currency: Union[currency_interface, Dict[str, float]]
    ) -> bool:
        return is_smaller_or_equal(self, currency)
