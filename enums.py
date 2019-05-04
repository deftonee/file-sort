from __future__ import annotations

import os
import shutil

from enum import Enum
from gettext import gettext as _
from typing import Dict, Callable

from file_classes import ImageFile, File


class MyEnum(Enum):

    @classmethod
    def values(cls) -> Dict[Enum, str]:
        raise NotImplemented()

    @classmethod
    def get_default(cls) -> Enum:
        raise NotImplemented()

    @classmethod
    def to_text(cls, value: Enum) -> str:
        return cls.values().get(value, '')

    @classmethod
    def to_value(cls, text: str) -> Enum:
        return next(
            (k for k, v in cls.values().items() if v == text),
            cls.get_default())


class EnumWithAction(MyEnum):
    @classmethod
    def handlers(cls) -> Dict[Enum, Callable]:
        raise NotImplemented()


class SortMethodEnum(EnumWithAction):
    """ What to do with files """
    COPY = 1
    MOVE = 2

    @classmethod
    def values(cls) -> Dict[SortMethodEnum, str]:
        return {
            SortMethodEnum.COPY: _('Copy'),
            SortMethodEnum.MOVE: _('Move'),
        }

    @classmethod
    def get_default(cls) -> SortMethodEnum:
        return SortMethodEnum.COPY

    @classmethod
    def handlers(cls) -> Dict[SortMethodEnum, Callable]:
        return {
            SortMethodEnum.COPY: cls.copy_handler,
            SortMethodEnum.MOVE: cls.move_handler,
        }

    @classmethod
    def copy_handler(cls, file_path, new_file_dir):
        shutil.copy2(file_path, new_file_dir)

    @classmethod
    def move_handler(cls, file_path, new_file_dir):
        shutil.move(file_path, new_file_dir, shutil.copy2)


class ConflictResolveMethodEnum(EnumWithAction):
    """ What to do if file with same name already exists in dst folder """
    REPLACE = 1
    SAVE_ALL = 2
    DO_NOTHING = 3

    @classmethod
    def values(cls) -> Dict[ConflictResolveMethodEnum, str]:
        return {
            ConflictResolveMethodEnum.REPLACE:
                _('Replace'),
            ConflictResolveMethodEnum.SAVE_ALL:
                _('Save all files with different names'),
            ConflictResolveMethodEnum.DO_NOTHING:
                _('Do nothing'),
        }

    @classmethod
    def get_default(cls) -> ConflictResolveMethodEnum:
        return ConflictResolveMethodEnum.SAVE_ALL

    @classmethod
    def handlers(cls) -> Dict[ConflictResolveMethodEnum, Callable]:
        return {
            ConflictResolveMethodEnum.REPLACE: cls.replace_handler,
            ConflictResolveMethodEnum.SAVE_ALL: cls.save_all_handler,
            ConflictResolveMethodEnum.DO_NOTHING: cls.do_nothing_handler,
        }

    @classmethod
    def replace_handler(cls, file_path, new_file_dir):

        file_name, file_ext = os.path.splitext(os.path.basename(file_path))
        new_file_path = os.path.join(new_file_dir, f'{file_name}{file_ext}')

        if os.path.exists(new_file_path):
            os.remove(new_file_path)

    @classmethod
    def save_all_handler(cls, file_path, new_file_dir):
        # rename file with same name
        file_name, file_ext = os.path.splitext(os.path.basename(file_path))
        new_file_path = os.path.join(new_file_dir, f'{file_name}{file_ext}')

        if os.path.exists(new_file_path):
            tmp_path = new_file_path
            i = 2
            while os.path.exists(tmp_path):
                tmp_path = os.path.join(
                    new_file_dir,
                    f'{file_name} ({i}){file_ext}')
                i += 1
            os.rename(new_file_path, tmp_path)

    @classmethod
    def do_nothing_handler(cls, new_file_path):
        if os.path.exists(new_file_path):
            raise Exception()


class FolderCleanupOptionsEnum(EnumWithAction):
    """ Remove or leave empty folders """
    REMOVE = 1
    LEAVE = 2

    @classmethod
    def values(cls) -> Dict[FolderCleanupOptionsEnum, str]:
        return {
            FolderCleanupOptionsEnum.REMOVE: _('Remove'),
            FolderCleanupOptionsEnum.LEAVE: _('Leave'),
        }

    @classmethod
    def get_default(cls) -> FolderCleanupOptionsEnum:
        return FolderCleanupOptionsEnum.REMOVE

    @classmethod
    def handlers(cls) -> Dict[FolderCleanupOptionsEnum, Callable]:
        return {
            FolderCleanupOptionsEnum.REMOVE: cls.remove_handler,
            FolderCleanupOptionsEnum.LEAVE: lambda _cls: None,
        }

    @classmethod
    def remove_handler(cls, file_path, new_file_dir):
        old_file_dir = os.path.dirname(file_path)
        if not os.listdir(old_file_dir):
            os.rmdir(old_file_dir)


class HiddenOptionEnum(EnumWithAction):
    """ Process hidden files and folders """
    YES = 1
    NO = 2

    @classmethod
    def values(cls) -> Dict[HiddenOptionEnum, str]:
        return {
            HiddenOptionEnum.YES: _('Process hidden objects'),
            HiddenOptionEnum.NO: _('Not process hidden objects'),
        }

    @classmethod
    def get_default(cls) -> HiddenOptionEnum:
        return HiddenOptionEnum.YES


class ContentTypesEnum(MyEnum):

    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'
    TEXT = 'text'
    UNKNOWN = 'unknown'

    # not used ones
    # APPLICATION = 'application'
    # EXAMPLE = 'example'
    # MESSAGE = 'message'
    # MODEL = 'model'
    # MULTIPART = 'multipart'

    @classmethod
    def get_class(cls, value):
        classes = {
            ContentTypesEnum.IMAGE: ImageFile,
        }
        return classes.get(value, File)

    @classmethod
    def get_default(cls) -> ContentTypesEnum:
        return ContentTypesEnum.UNKNOWN


class LangEnum(MyEnum):
    EN = 'en_US'
    RU = 'ru_RU'

    @classmethod
    def values(cls) -> Dict[LangEnum, str]:
        return {
            LangEnum.EN: 'English',
            LangEnum.RU: 'Русский',
        }

    @classmethod
    def get_default(cls) -> LangEnum:
        return LangEnum.EN

    @classmethod
    def codes(cls):
        return {
            LangEnum.EN: (LangEnum.EN.value, 'UTF-8'),
            LangEnum.RU: (LangEnum.RU.value, 'UTF-8'),
        }
