import exifread
import os

from datetime import datetime
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
        return datetime.min


class ImageFile(File):
    """ Class with information about image file """
    def get_date(self) -> datetime:
        result = None
        with open(self.path, 'rb') as f:
            exif = exifread.process_file(f)

            if 'EXIF DateTimeDigitized' in exif:
                result = datetime.strptime(
                    exif['EXIF DateTimeDigitized'].values, DATE_PATTERN)
            elif 'EXIF DateTimeOriginal' in exif:
                result = datetime.strptime(
                    exif['EXIF DateTimeOriginal'].values, DATE_PATTERN)
            elif 'Image DateTime' in exif:
                result = datetime.strptime(
                    exif['Image DateTime'].values, DATE_PATTERN)
        if not result:
            result = super().get_date()
        return result
