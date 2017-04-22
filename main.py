
import logging
import magic
import os
import re
import shutil

from collections import OrderedDict
from datetime import datetime
from functools import wraps
from gettext import gettext as _
from PIL import Image


CONTENT_TYPE_TAGS = ('%T', )
EXTENSION_TAGS = ('%E', )
DATETIME_TAGS = ('%Y', '%m', '%d', '%H', '%M', '%S', '%z',
                 '%a', '%A', '%b', '%B', '%c', '%I', '%p')
ALL_TAGS = CONTENT_TYPE_TAGS + EXTENSION_TAGS + DATETIME_TAGS

TAG_PATTERN = '%[a-zA-Z]'
PATH_DELIMITER = '/'
FORMAT_HELP = _('''
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
''')

logger = logging.getLogger('sort process')
logger.setLevel(logging.INFO)


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
        APPLICATION: DEFAULT_FOLDER_NAME,
        EXAMPLE: DEFAULT_FOLDER_NAME,
        MESSAGE: DEFAULT_FOLDER_NAME,
        MODEL: DEFAULT_FOLDER_NAME,
        MULTIPART: DEFAULT_FOLDER_NAME,
    }

    classes = {
        IMAGE: ImageFile,
        VIDEO: DEFAULT_CLASS,
        APPLICATION: DEFAULT_CLASS,
        AUDIO: DEFAULT_CLASS,
        EXAMPLE: DEFAULT_CLASS,
        MESSAGE: DEFAULT_CLASS,
        MODEL: DEFAULT_CLASS,
        MULTIPART: DEFAULT_CLASS,
        TEXT: DEFAULT_CLASS,
    }

CTE = ContentTypesEnum


def logged(fn):
    @wraps(fn)
    def _inner(name):

        logger.info(
            'Start processing of "%s"' % name)
        try:
            fn(name)
        except (OSError, ) as e:
            logger.error(e)
        else:
            logger.info('Done')

    return _inner


def sort(src_path, dst_path, path_format):
    """
    Sort files from src_path and place them in dst_path according to path_format
    :param src_path:
    :param dst_path:
    :param path_format:
    :return:
    """
    path_structure = []

    def process_folder(folder_path):
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

    @logged
    def process_file(file_path):
        """ Process file """
        mime_info = magic.from_file(file_path, mime=True) or ''
        file_type = mime_info.split('/')[0]

        file_obj = CTE.classes.get(
            file_type, CTE.DEFAULT_CLASS
        )(
            file_path, file_type
        )

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

        new_file_path = os.path.join(*new_path_parts)

        if not os.path.exists(new_file_path):
            os.makedirs(new_file_path)
        shutil.copy2(file_path, new_file_path)

    for part in path_format.split(PATH_DELIMITER):
        path_structure.append((part, set(re.findall(TAG_PATTERN, part))))

    for result in process_folder(src_path):
        yield result


def validate(src_path, dst_path, path_format):
    if not os.path.isdir(src_path):
        return False, _('Source folder path is not valid')
    if not os.path.isdir(dst_path):
        return False, _('Destination folder path is not valid')

    if (
            not path_format
            or not set(re.findall(TAG_PATTERN, path_format)).issubset(ALL_TAGS)
    ):
        return False, _('Path format is not valid')

    return True, ''
