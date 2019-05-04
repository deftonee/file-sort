from __future__ import annotations

import json
import os
from enum import Enum

SETTINGS_FILENAME = 'settings.json'


class SettingEnum(Enum):
    SRC = 'src'
    DST = 'dst'
    FMT = 'fmt'
    LNG = 'lng'

    @staticmethod
    def list_handler(vault: Dict, key: str, value: str):
        values = vault.setdefault(key, [])
        values.insert(0, value)

    @staticmethod
    def str_handler(vault: Dict, key: str, value: str):
        vault[key] = value

    @classmethod
    def handlers(cls):
        """ Functions that set value """
        return {
            SettingEnum.SRC: SettingEnum.list_handler,
            SettingEnum.DST: SettingEnum.list_handler,
            SettingEnum.FMT: SettingEnum.list_handler,
            SettingEnum.LNG: SettingEnum.str_handler,
        }


class Settings:
    """ Saves choices user made """
    instance: Settings = None

    def __new__(cls, folder):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, folder):
        self.settings_path = os.path.join(folder, SETTINGS_FILENAME)
        self._settings = {}
        self.load()

    def load(self):
        try:
            with open(self.settings_path, 'r') as settings_file:
                self._settings = json.load(settings_file)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            pass

    def save(self):
        with open(self.settings_path, 'w') as settings_file:
            json.dump(self._settings, settings_file)

    def get(self, name: SettingEnum, default=None):
        return self._settings.get(name.value, default)

    def set(self, name: SettingEnum, value):
        SettingEnum.handlers()[name](self._settings, name.value, value)
