# coding: utf-8

import logging
import magic
import re
import os
import shutil

from datetime import datetime
from gettext import gettext as _
from PIL import Image


# %t or %T is a content type of file
# %e or %E is a extension of file
CONTENT_TYPE_TAGS = (u'%t', u'%T')
EXTENSION_TAGS = (u'%e', u'%E')
DATETIME_TAGS = (u'%a', u'%A', u'%w', u'%d', u'%b', u'%B', u'%m', u'%y', u'%Y',
                 u'%H', u'%I', u'%p', u'%M', u'%S', u'%f', u'%z', u'%Z', u'%j',
                 u'%U', u'%W', u'%c', u'%x', u'%X', )
ALL_TAGS = CONTENT_TYPE_TAGS + EXTENSION_TAGS + DATETIME_TAGS

TAG_PATTERN = u'%[a-zA-Z]'
PATH_DELIMITER = u'/'


class File(object):
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
            exif = im._getexif() or {}
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


class ContentTypesEnum(object):

    IMAGE = u'image'
    VIDEO = u'video'
    APPLICATION = u'application'
    AUDIO = u'audio'
    EXAMPLE = u'example'
    MESSAGE = u'message'
    MODEL = u'model'
    MULTIPART = u'multipart'
    TEXT = u'text'

    DEFAULT_FOLDER_NAME = _(u'Others')
    DEFAULT_CLASS = File

    folder_names = {
        IMAGE: _(u'Images'),
        VIDEO: _(u'Videos'),
        APPLICATION: DEFAULT_FOLDER_NAME,
        AUDIO: DEFAULT_FOLDER_NAME,
        EXAMPLE: DEFAULT_FOLDER_NAME,
        MESSAGE: DEFAULT_FOLDER_NAME,
        MODEL: DEFAULT_FOLDER_NAME,
        MULTIPART: DEFAULT_FOLDER_NAME,
        TEXT: DEFAULT_FOLDER_NAME,
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
                except (OSError, ), e:
                    logging.error(
                        u'Error while processing of "%s":\n%s' % (
                            current_path, e))
                else:
                    logging.info(
                        u'Done processing of "%s"' % current_path)
            elif os.path.isdir(current_path):
                process_folder(current_path)

    def process_file(file_path):
        """ Process file """
        mime_info = magic.from_file(file_path, mime=True) or u''
        file_type = mime_info.split(u'/')[0]

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
                    lvl = lvl.replace(u'%e', u'%E').replace(
                        u'%E',
                        file_obj.extension
                    )

                if lvl_tags.intersection(CONTENT_TYPE_TAGS):
                    lvl = lvl.replace(u'%t', u'%T').replace(
                        u'%T',
                        CTE.folder_names.get(
                            file_obj.content_type,
                            CTE.DEFAULT_FOLDER_NAME)
                    )

                if lvl_tags.intersection(DATETIME_TAGS):
                    lvl = file_obj.date.strftime(lvl)

                new_path_parts.append(lvl.decode('UTF-8'))

        new_file_path = os.path.join(*new_path_parts)

        if not os.path.exists(new_file_path):
            os.makedirs(new_file_path)
        shutil.copy2(file_path, new_file_path)

    for part in path_format.split(PATH_DELIMITER):
        path_structure.append((part, set(re.findall(TAG_PATTERN, part))))

    process_folder(src_path)


def validate(src_path, dst_path, path_format):
    if not os.path.isdir(src_path):
        return False, _(u'Source folder path is not valid')
    if not os.path.isdir(dst_path):
        return False, _(u'Destination folder path is not valid')

    if (
            not path_format
            or not set(re.findall(TAG_PATTERN, path_format)).issubset(ALL_TAGS)
    ):
        return False, _(u'Path format is not valid')

    return True, u''
