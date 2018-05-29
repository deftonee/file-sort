
import locale
import magic
import os
import re
import shutil
import sys

from typing import Tuple, Iterator
from datetime import datetime
from gettext import gettext as _, bindtextdomain

from PIL import Image


# settings for translation
bindtextdomain('messages', os.path.join(os.path.dirname(sys.argv[0]), 'locale'))
os.environ['LANGUAGE'] = '.'.join(locale.getdefaultlocale())

# constants
CONTENT_TYPE_TAGS = ('%T', )
EXTENSION_TAGS = ('%E', )
DATETIME_TAGS = ('%Y', '%m', '%d', '%H', '%M', '%S', '%z',
                 '%a', '%A', '%b', '%B', '%c', '%I', '%p')
ALL_TAGS = CONTENT_TYPE_TAGS + EXTENSION_TAGS + DATETIME_TAGS

TAG_PATTERN = '%[a-zA-Z]'
PATH_DELIMITER = '/'
FORMAT_HELP = _('''
    /  - Folder structure separator
    %T - Content type name of file (Images, Videos, ...)
    %E - Extension of file (jpg, png, doc, avi, ...)
    %Y - Year with century as a decimal number
    %m - Month as a decimal number [01,12]
    %d - Day of the month as a decimal number [01,31]
    %H - Hour (24-hour clock) as a decimal number [00,23]
    %M - Minute as a decimal number [00,59]
    %S - Second as a decimal number [00,61]
    %z - Time zone offset from UTC
    %a - Locale's abbreviated weekday name
    %A - Locale's full weekday name
    %b - Locale's abbreviated month name
    %B - Locale's full month name
    %c - Locale's appropriate date and time representation
    %I - Hour (12-hour clock) as a decimal number [01,12]
    %p - Locale's equivalent of either AM or PM
    
    Format example: %T/%Y/%m%B - %d
    Path example for this format: Images/2017/05May - 02/    
''')


class File:
    path = None
    content_type = None
    extension = None
    date = None
    supported_tags = None

    def __init__(self, _path, _type):
        self.path = _path
        self.content_type = _type
        self.extension = os.path.splitext(_path)[1].strip('.')
        self.date = self.get_date()
        self.supported_tags = self.get_supported_tags()

    def get_date(self):
        if os.path.getmtime(self.path):
            return datetime.fromtimestamp(os.path.getmtime(self.path))
        elif os.path.getctime(self.path):
            return datetime.fromtimestamp(os.path.getctime(self.path))

    def get_supported_tags(self):
        result = ()
        if self.content_type:
            result += CONTENT_TYPE_TAGS
        if self.extension:
            result += EXTENSION_TAGS
        if self.date:
            result += DATETIME_TAGS
        return result


class ImageFile(File):

    def get_date(self):
        try:
            im = Image.open(self.path)
            exif = getattr(im, '_getexif', dict)() or {}
        except IOError:
            return

        if 0x9003 in exif:  # DateTimeDigitized
            return datetime.strptime(exif.get(0x9003), '%Y:%m:%d %H:%M:%S')
        elif 0x9004 in exif:  # DateTimeOriginal
            return datetime.strptime(exif.get(0x9004), '%Y:%m:%d %H:%M:%S')
        elif 0x0132 in exif:  # DateTime
            return datetime.strptime(exif.get(0x0132), '%Y:%m:%d %H:%M:%S')
        elif os.path.getmtime(self.path):
            return datetime.fromtimestamp(os.path.getmtime(self.path))


class Enum:
    values = {}
    default_key = None

    @classmethod
    def get_by_value(cls, value):
        return next(
            (k for k, v in cls.values.items() if v == value),
            cls.default_key
        )


class SortMethodEnum(Enum):
    """ What to do with files """
    COPY = 1
    MOVE = 2
    default_key = COPY

    values = {
        COPY: _('Copy'),
        MOVE: _('Move'),
    }


class ConflictResolveMethodEnum(Enum):
    """ What to do if file with same name already exists in dst folder """
    REPLACE = 1
    SAVE_ALL = 2
    DO_NOTHING = 3
    default_key = SAVE_ALL

    values = {
        REPLACE: _('Replace'),
        SAVE_ALL: _('Save all files with different names'),
        DO_NOTHING: _('Do nothing'),
    }


class FolderCleanupOptionsEnum(Enum):
    """ Remove or leave empty folders """
    REMOVE = 1
    LEAVE = 2
    default_key = LEAVE

    values = {
        REMOVE: _('Remove'),
        LEAVE: _('Leave'),
    }


class HiddenOptionEnum(Enum):
    """ Process hidden files and folders """
    YES = 1
    NO = 2
    default_key = NO

    values = {
        YES: _('Process hidden objects'),
        NO: _('Not process hidden objects'),
    }


class ContentTypesEnum:

    IMAGE = 'image'
    VIDEO = 'video'
    APPLICATION = 'application'
    AUDIO = 'audio'
    EXAMPLE = 'example'
    MESSAGE = 'message'
    MODEL = 'model'
    MULTIPART = 'multipart'
    TEXT = 'text'

    DEFAULT_FOLDER_NAME = _('Others')
    DEFAULT_CLASS = File

    folder_names = {
        IMAGE: _('Images'),
        VIDEO: _('Videos'),
        AUDIO: _('Audios'),
        TEXT: _('Documents'),
    }

    classes = {
        IMAGE: ImageFile,
    }


CTE = ContentTypesEnum
CRE = ConflictResolveMethodEnum


def sort(src_path: str, dst_path: str,
         path_format: str, method: int,
         conflict_resolve_method: int,
         cleanup_option: int) -> Iterator[Tuple[bool, str]]:
    """
    Sort files from src_path and place them in dst_path according to path_format
    """
    path_structure = []

    def process_folder(folder_path: str) -> Iterator[Tuple[bool, str]]:
        """ Process folder """
        if not os.path.isdir(folder_path):
            return
        for name in os.listdir(folder_path):
            current_path = os.path.join(folder_path, name)
            if os.path.isfile(current_path):
                try:
                    process_file(current_path)
                except Exception as e:
                    yield False, current_path
                else:
                    yield True, current_path
            elif os.path.isdir(current_path):
                for result in process_folder(current_path):
                    yield result

    def process_file(file_path: str) -> None:
        """ Process file """

        # constructing file's new path
        mime_info = magic.from_file(file_path, mime=True) or ''
        file_type = mime_info.split('/')[0]
        file_obj = CTE.classes.get(file_type, CTE.DEFAULT_CLASS)(
            file_path, file_type)

        new_path_parts = [dst_path]
        for lvl, lvl_tags in path_structure:
            if not lvl_tags.issubset(file_obj.supported_tags):
                new_path_parts.append(CTE.DEFAULT_FOLDER_NAME)
            else:
                if lvl_tags.intersection(EXTENSION_TAGS):
                    lvl = lvl.replace('%e', '%E').replace(
                        '%E',
                        file_obj.extension
                    )

                if lvl_tags.intersection(CONTENT_TYPE_TAGS):
                    lvl = lvl.replace('%t', '%T').replace(
                        '%T',
                        CTE.folder_names.get(
                            file_obj.content_type,
                            CTE.DEFAULT_FOLDER_NAME)
                    )

                if lvl_tags.intersection(DATETIME_TAGS):
                    lvl = file_obj.date.strftime(lvl)

                new_path_parts.append(lvl)

        new_file_dir = os.path.join(*new_path_parts)

        file_name, file_ext = os.path.splitext(os.path.basename(file_path))

        new_file_path = os.path.join(
            new_file_dir,
            '%s%s' % (file_name, file_ext))

        if not os.path.exists(new_file_dir):
            os.makedirs(new_file_dir)

        # resolving conflict if file already exists
        if os.path.exists(new_file_path):
            if conflict_resolve_method == CRE.REPLACE:
                os.remove(new_file_path)
            elif conflict_resolve_method == CRE.SAVE_ALL:
                i = 2
                while os.path.exists(new_file_path):
                    new_file_path = os.path.join(
                        new_file_dir,
                        '%s (%s)%s' % (file_name, i, file_ext))
                    i += 1
            elif conflict_resolve_method == CRE.DO_NOTHING:
                return

        # doing main job
        if method == SortMethodEnum.COPY:
            shutil.copy2(file_path, new_file_dir)
        elif method == SortMethodEnum.MOVE:
            shutil.move(file_path, new_file_dir, shutil.copy2)

        # delete empty old folder if needed
        if cleanup_option == FolderCleanupOptionsEnum.REMOVE:
            old_file_dir = os.path.dirname(file_path)
            if not os.listdir(old_file_dir):
                os.rmdir(old_file_dir)

    for part in path_format.split(PATH_DELIMITER):
        path_structure.append((part, set(re.findall(TAG_PATTERN, part))))

    for result in process_folder(src_path):
        yield result


def validate(src_path: str, dst_path: str,
             path_format: str, method: int,
             conflict_resolve_method: int,
             cleanup_option: int) -> Tuple[bool, str]:
    """ check all input parameters """
    if not os.path.isdir(src_path):
        return False, _('Source folder path is not valid')
    if not os.path.isdir(dst_path):
        return False, _('Destination folder path is not valid')

    if (not path_format or
            not set(re.findall(TAG_PATTERN, path_format)).issubset(ALL_TAGS)):
        return False, _('Path format is not valid')

    if method not in SortMethodEnum.values:
        return False, _('Sorting method is not valid')

    if conflict_resolve_method not in ConflictResolveMethodEnum.values:
        return False, _('Conflict resolving method is not valid')

    if cleanup_option not in FolderCleanupOptionsEnum.values:
        return False, _('Remove empty folders option is not valid')

    return True, ''
