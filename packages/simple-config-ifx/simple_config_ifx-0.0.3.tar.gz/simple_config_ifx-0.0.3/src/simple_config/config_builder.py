from typing import TypeVar, Any
import os
import json
from simple_config.config import Configuration


KeyType = TypeVar('KeyType')

def _deep_update(mapping: dict[KeyType, Any], updating_mapping: dict[KeyType, Any]) -> dict[KeyType, Any]:
    updated_mapping = mapping.copy()
    for k, v in updating_mapping.items():
        if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
            updated_mapping[k] = _deep_update(updated_mapping[k], v)
        else:
            updated_mapping[k] = v
    return updated_mapping

def _deep_strip(mapping: dict[KeyType, Any]) -> dict[KeyType, Any]:
    striped_mapping = {}
    for k, v in mapping.items():
        if k.startswith("-"):
            continue
        if isinstance(v, dict):
            v = _deep_strip(v)
        striped_mapping[k] = v
    return striped_mapping



class ConfigurationBuilder:
    def __init__(self, base_path: str = ""):
        self._base_path: str = base_path
        self._config_json = {}

    def set_base_path(self, base_path: str) -> "ConfigurationBuilder":
        self._base_path = base_path
        return self

    def add_json_file(self, filename: str, optional: bool = False) -> "ConfigurationBuilder":
        try:
            with open(os.path.join(self._base_path, filename)) as f:
                new_config = json.load(f)
                self._config_json = _deep_update(self._config_json, _deep_strip(new_config))
        except FileNotFoundError as e:
            if not optional:
                raise FileNotFoundError(e)
        return self

    def build(self) -> "Configuration":
        return Configuration(self._config_json)


__all__ = ["ConfigurationBuilder"]