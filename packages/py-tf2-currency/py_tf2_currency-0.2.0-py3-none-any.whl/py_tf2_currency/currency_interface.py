from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class currency_interface:
    keys: float
    metal: float

    def to_dict(self) -> Dict[str, Any]:
        return {"keys": self.keys, "metal": self.metal}
