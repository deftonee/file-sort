# coding: utf-8

import datetime
import logging
import re
import os
import shutil
import sys

import magic
from PIL import Image


# %t or %T is a content type of file
# %e or %E is a extension of file

src_path = sys.argv[1]
dst_path = sys.argv[2]
path_format = sys.argv[3]

# src_path = u'/Users/deftone/src'
# dst_path = u'/Users/deftone/dst'
# path_format = u'%T/%Y/%m-%B.%d'


path_structure = []

for part in path_format.split(u'/'):
    path_structure.append((part, set(re.findall(ur'%[a-zA-Z]', part))))

content_type_tags = (u'%t', u'%T')
extension_tags = (u'%e', u'%E')
datetime_tags = (u'%a', u'%A', u'%w', u'%d', u'%b', u'%B', u'%m', u'%y', u'%Y',
                 u'%H', u'%I', u'%p', u'%M', u'%S', u'%f', u'%z', u'%Z', u'%j',
                 u'%U', u'%W', u'%c', u'%x', u'%X', )


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
            return datetime.datetime.fromtimestamp(os.path.getmtime(self.path))
        elif os.path.getctime(self.path):
            return datetime.datetime.fromtimestamp(os.path.getctime(self.path))

    def get_supported_tags(self):
        result = ()
        if self.content_type:
            result += content_type_tags
        if self.extension:
            result += extension_tags
        if self.date:
            result += datetime_tags
        return set(result)


class ImageFile(File):

    def get_date(self):
        try:
            im = Image.open(self.path)
            exif = im._getexif() or {}
        except IOError:
            return

        if 0x9003 in exif:  # DateTimeDigitized
            return datetime.datetime.strptime(exif.get(0x9003), '%Y:%m:%d %H:%M:%S')
        elif 0x9004 in exif:  # DateTimeOriginal
            return datetime.datetime.strptime(exif.get(0x9004), '%Y:%m:%d %H:%M:%S')
        elif 0x0132 in exif:  # DateTime
            return datetime.datetime.strptime(exif.get(0x0132), '%Y:%m:%d %H:%M:%S')
        elif os.path.getmtime(self.path):
            return datetime.datetime.fromtimestamp(os.path.getmtime(self.path))


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

    DEFAULT_FOLDER_NAME = u'Others'
    DEFAULT_CLASS = File

    folder_names = {
        IMAGE: u'Images',
        VIDEO: u'Videos',
        APPLICATION: DEFAULT_FOLDER_NAME,
        AUDIO: DEFAULT_FOLDER_NAME,
        EXAMPLE: DEFAULT_FOLDER_NAME,
        MESSAGE: DEFAULT_FOLDER_NAME,
        MODEL: DEFAULT_FOLDER_NAME,
        MULTIPART: DEFAULT_FOLDER_NAME,
        TEXT: DEFAULT_FOLDER_NAME,
    }

    class_names = {
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


def process_folder(folder_path):
    if not os.path.isdir(folder_path):
        return
    for file_name in os.listdir(folder_path):
        current_path = os.path.join(folder_path, file_name)
        if os.path.isfile(current_path):
            process_file(current_path)
        elif os.path.isdir(current_path):
            process_folder(current_path)


def process_file(file_path):

    mime_info = magic.from_file(file_path, mime=True) or u''
    file_type = mime_info.split(u'/')[0]

    file_obj = CTE.class_names.get(
        file_type, CTE.DEFAULT_CLASS
    )(
        file_path, file_type
    )

    new_path_parts = [dst_path]

    for lvl, lvl_tags in path_structure:

        if not lvl_tags.issubset(file_obj.supported_tags):
            new_path_parts.append(CTE.DEFAULT_FOLDER_NAME)
        else:
            if lvl_tags.intersection(extension_tags):
                lvl = lvl.replace(u'%e', u'%E').replace(
                    u'%E',
                    file_obj.extension
                )

            if lvl_tags.intersection(content_type_tags):
                lvl = lvl.replace(u'%t', u'%T').replace(
                    u'%T',
                    CTE.folder_names.get(file_obj.content_type, CTE.DEFAULT_FOLDER_NAME)
                )

            if lvl_tags.intersection(datetime_tags):
                lvl = file_obj.date.strftime(lvl)

            new_path_parts.append(lvl)

    new_file_path = os.path.join(*new_path_parts)

    if not os.path.exists(new_file_path):
        os.makedirs(new_file_path)
    shutil.copy2(file_path, new_file_path)


process_folder(src_path)


# DateTime 0x0132
# DateTimeDigitized 0x9003
# DateTimeOriginal 0x9004
# PreviewDateTime 0xc71b

