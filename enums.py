from enum import Enum
from gettext import gettext as _

from file_classes import ImageFile, File


DEFAULT_FOLDER_NAME = _('Others')


class MyEnum(Enum):

    @classmethod
    def values(cls):
        return {}

    @classmethod
    def get_default(cls):
        raise NotImplemented()

    @classmethod
    def to_text(cls, value):
        return cls.values().get(value)

    @classmethod
    def to_value(cls, text):
        return next(
            (k for k, v in cls.values().items() if v == text),
            cls.get_default()
        )


class SortMethodEnum(MyEnum):
    """ What to do with files """
    COPY = 1
    MOVE = 2

    @classmethod
    def values(cls):
        return {
            SortMethodEnum.COPY: _('Copy'),
            SortMethodEnum.MOVE: _('Move'),
        }

    @classmethod
    def get_default(cls):
        return SortMethodEnum.COPY


class ConflictResolveMethodEnum(MyEnum):
    """ What to do if file with same name already exists in dst folder """
    REPLACE = 1
    SAVE_ALL = 2
    DO_NOTHING = 3

    @classmethod
    def values(cls):
        return {
            ConflictResolveMethodEnum.REPLACE:
                _('Replace'),
            ConflictResolveMethodEnum.SAVE_ALL:
                _('Save all files with different names'),
            ConflictResolveMethodEnum.DO_NOTHING:
                _('Do nothing'),
        }

    @classmethod
    def get_default(cls):
        return ConflictResolveMethodEnum.SAVE_ALL


class FolderCleanupOptionsEnum(MyEnum):
    """ Remove or leave empty folders """
    REMOVE = 1
    LEAVE = 2

    @classmethod
    def values(cls):
        return {
            FolderCleanupOptionsEnum.REMOVE: _('Remove'),
            FolderCleanupOptionsEnum.LEAVE: _('Leave'),
        }

    @classmethod
    def get_default(cls):
        return FolderCleanupOptionsEnum.REMOVE


class HiddenOptionEnum(MyEnum):
    """ Process hidden files and folders """
    YES = 1
    NO = 2

    @classmethod
    def values(cls):
        return {
            HiddenOptionEnum.YES: _('Process hidden objects'),
            HiddenOptionEnum.NO: _('Not process hidden objects'),
        }

    @classmethod
    def get_default(cls):
        return HiddenOptionEnum.YES


class ContentTypesEnum(MyEnum):

    IMAGE = 'image'
    VIDEO = 'video'
    APPLICATION = 'application'
    AUDIO = 'audio'
    EXAMPLE = 'example'
    MESSAGE = 'message'
    MODEL = 'model'
    MULTIPART = 'multipart'
    TEXT = 'text'

    @classmethod
    def get_class(cls, value):
        classes = {
            ContentTypesEnum.IMAGE: ImageFile,
        }
        return classes.get(value, File)


SME = SortMethodEnum
CRE = ConflictResolveMethodEnum
FCE = FolderCleanupOptionsEnum
HOE = HiddenOptionEnum
CTE = ContentTypesEnum
