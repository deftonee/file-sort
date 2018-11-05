import os

from datetime import datetime
from PIL import Image
from typing import Text


DATE_PATTERN = '%Y:%m:%d %H:%M:%S'


class File:
    """ Class with information about file """
    def __init__(self, _path: Text, _type):
        self.path = _path
        self.content_type = _type
        self.extension = os.path.splitext(_path)[1].strip('.')
        self.date = self.get_date()

    def get_date(self) -> datetime:
        if os.path.getmtime(self.path):
            return datetime.fromtimestamp(os.path.getmtime(self.path))
        elif os.path.getctime(self.path):
            return datetime.fromtimestamp(os.path.getctime(self.path))


class ImageFile(File):
    """ Class with information about image file """
    def get_date(self) -> datetime:
        result = datetime.min
        try:
            im = Image.open(self.path)
            exif = getattr(im, '_getexif', dict)() or {}
        except IOError:
            pass
        else:
            if 0x9003 in exif:  # DateTimeDigitized
                result = datetime.strptime(exif.get(0x9003), DATE_PATTERN)
            elif 0x9004 in exif:  # DateTimeOriginal
                result = datetime.strptime(exif.get(0x9004), DATE_PATTERN)
            elif 0x0132 in exif:  # DateTime
                result = datetime.strptime(exif.get(0x0132), DATE_PATTERN)
            elif os.path.getmtime(self.path):
                result = datetime.fromtimestamp(os.path.getmtime(self.path))
        return result
