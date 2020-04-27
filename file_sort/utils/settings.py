from __future__ import annotations

import json
import os
from enum import Enum
from typing import Dict, Optional

SETTINGS_REL_PATH = '../../settings.json'
SETTINGS_PATH = os.path.join(
    os.path.dirname(__file__),
    SETTINGS_REL_PATH,
)


class SettingEnum(Enum):
    SRC = 'src'
    DST = 'dst'
    FMT = 'fmt'
    OPTIONS = 'options'
    METHOD = 'method'
    CONFLICT = 'conflict'
    CLEANUP = 'cleanup'
    LNG = 'lng'

    @staticmethod
    def multiple_values_handler(vault: Dict, key: str, value: str):
        values = vault.setdefault(key, [])
        if value not in values:
            values.insert(0, value)

    @staticmethod
    def single_value_handler(vault: Dict, key: str, value: str):
        vault[key] = value

    @classmethod
    def handlers(cls):
        """ Functions that set value """
        return {
            SettingEnum.SRC: SettingEnum.multiple_values_handler,
            SettingEnum.DST: SettingEnum.multiple_values_handler,
            SettingEnum.FMT: SettingEnum.multiple_values_handler,
            SettingEnum.OPTIONS: SettingEnum.single_value_handler,
            SettingEnum.METHOD: SettingEnum.single_value_handler,
            SettingEnum.CONFLICT: SettingEnum.single_value_handler,
            SettingEnum.CLEANUP: SettingEnum.single_value_handler,
            SettingEnum.LNG: SettingEnum.single_value_handler,
        }


class Settings:
    """ Saves choices user made """
    __instance: Optional[Settings] = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls._storage = {}
            cls._load()
        return cls.__instance

    @classmethod
    def _load(cls):
        try:
            with open(SETTINGS_PATH, 'r') as settings_file:
                cls._storage = json.load(settings_file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

    def save(self):
        with open(SETTINGS_PATH, 'w') as settings_file:
            json.dump(self._storage, settings_file)

    def get(self, name: SettingEnum, default=None):
        return self._storage.get(name.value, default)

    def set(self, name: SettingEnum, value):
        SettingEnum.handlers()[name](self._storage, name.value, value)
