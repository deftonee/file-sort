# coding: utf-8

import logging
from os import listdir, path, makedirs
import shutil
import sys
import magic

from datetime import datetime, date


from PIL import Image

path_format = '%Y/%m.%d'

src_path = sys.argv[1]
dst_path = sys.argv[2]

# src_path = u'/Users/deftone/src'
# dst_path = u'/Users/deftone/dst'


class ContentTypesEnum(object):

    IMAGE = 'image'
    VIDEO = 'video'
    APPLICATION = 'application'
    AUDIO = 'audio'
    EXAMPLE = 'example'
    MESSAGE = 'message'
    MODEL = 'model'
    MULTIPART = 'multipart'
    TEXT = 'text'

    DEFAULT_FOLDER_NAME = 'Others'

    folder_names = {
        IMAGE: 'Images',
        VIDEO: 'Videos',
        APPLICATION: DEFAULT_FOLDER_NAME,
        AUDIO: DEFAULT_FOLDER_NAME,
        EXAMPLE: DEFAULT_FOLDER_NAME,
        MESSAGE: DEFAULT_FOLDER_NAME,
        MODEL: DEFAULT_FOLDER_NAME,
        MULTIPART: DEFAULT_FOLDER_NAME,
        TEXT: DEFAULT_FOLDER_NAME,
    }

CTE = ContentTypesEnum


def process_folder(folder_path, fn):
    if not path.isdir(folder_path):
        return
    for file_name in listdir(folder_path):
        current_path = path.join(folder_path, file_name)
        if path.isfile(current_path):
            fn(current_path)
        elif path.isdir(current_path):
            process_folder(current_path, fn)


def get_date_from_exif(exif, key):
    if key in exif:
        return datetime.strptime(exif.get(key), '%Y:%m:%d %H:%M:%S')
    else:
        return None


def process_image(file_path):
    try:
        im = Image.open(file_path)
        exif = im._getexif() or {}
    except IOError:
        return

    file_date = None
    if 0x9003 in exif:  # DateTimeDigitized
        file_date = datetime.strptime(exif.get(0x9003), '%Y:%m:%d %H:%M:%S')
    elif 0x9004 in exif:  # DateTimeOriginal
        file_date = datetime.strptime(exif.get(0x9004), '%Y:%m:%d %H:%M:%S')
    elif 0x0132 in exif:  # DateTime
        file_date = datetime.strptime(exif.get(0x0132), '%Y:%m:%d %H:%M:%S')
    elif path.getmtime(file_path):
        file_date = datetime.fromtimestamp(path.getmtime(file_path))
    return file_date


def get_dst_path_for_file(file_path):

    params = [dst_path]

    mime_info = magic.from_file(file_path, mime=True) or ''
    file_type = mime_info.split('/')[0]

    if file_type == CTE.IMAGE:
        file_date = process_image(file_path)
        params.append(CTE.folder_names.get(file_type, CTE.DEFAULT_FOLDER_NAME))
        if isinstance(file_date, date):
            params.extend([unicode(file_date.strftime(f)) for f in path_format.split(u'/')])
    else:
        params.append(CTE.folder_names.get(file_type, CTE.DEFAULT_FOLDER_NAME))

    return path.join(*params)


def process_file(file_path):

    new_file_path = get_dst_path_for_file(file_path)

    if not path.isdir(new_file_path):
        makedirs(new_file_path)
    shutil.copy2(file_path, new_file_path)


process_folder(src_path, process_file)


# DateTime 0x0132
# DateTimeDigitized 0x9003
# DateTimeOriginal 0x9004
# PreviewDateTime 0xc71b

