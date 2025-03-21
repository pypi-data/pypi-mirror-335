from typing import Optional, Dict, Any


class Vault:
    """ """
    def __init__(self, values: Optional[dict] = None):
        self._values = values or {}

    @property
    def values(self) -> dict:
        return self._values

    def get(self, name: str) -> Optional[Any]:
        return self._values.get(name, None)
