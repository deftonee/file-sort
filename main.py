import logging
import os
import re
import traceback

from typing import Tuple, Iterator, Text, List, Set
from gettext import gettext as _

from enums import (
    SortMethodEnum, FolderCleanupOptionsEnum, ContentTypesEnum,
    ConflictResolveMethodEnum)
from helpers import set_locale, TagProcessor

try:
    import magic
except ImportError:
    magic = None

logging.basicConfig(filename="log.log", level=logging.INFO)

set_locale()

# constants
PATH_DELIMITER = '/'
TAG_PATTERN = '%[a-zA-Z]'


class Sorter:
    def __init__(self, src_path: str, dst_path: str, path_format: str,
                 method: SortMethodEnum,
                 conflict_resolve_method: ConflictResolveMethodEnum,
                 cleanup_option: FolderCleanupOptionsEnum):
        self.src_path = src_path
        self.dst_path = dst_path
        self.method = method
        self.conflict_resolve_method = conflict_resolve_method
        self.cleanup_option = cleanup_option

        self.path_structure: List[Tuple[Text, Set[Text]]] = []
        for part in path_format.split(PATH_DELIMITER):
            self.path_structure.append(
                (part, set(re.findall(TAG_PATTERN, part))))

    def sort(self) -> Iterator[Tuple[bool, str]]:
        """
        Sort files from src_path and place them in dst_path
        according to path_format
        """
        for result in self._process_folder(self.src_path):
            yield result

    def validate_paths(self) -> Tuple[bool, str]:
        """ Check correctness of paths """
        if not os.path.isdir(self.src_path):
            return False, _('Source folder path is not valid')
        if not os.path.isdir(self.dst_path):
            return False, _('Destination folder path is not valid')
        return True, ''

    def _process_folder(self, folder_path: str) -> Iterator[Tuple[bool, str]]:
        """ Process folder """
        if not os.path.isdir(folder_path):
            return
        for name in os.listdir(folder_path):
            current_path = os.path.join(folder_path, name)
            if os.path.isfile(current_path):
                try:
                    self._process_file(current_path)
                except Exception as e:  # TODO specify kinds of error
                    logging.error(traceback.format_exc())
                    yield False, current_path
                else:
                    yield True, current_path
            elif os.path.isdir(current_path):
                for result in self._process_folder(current_path):
                    yield result

    def _process_file(self, file_path: str) -> None:
        """ Process file """
        # defining type of file
        if magic is not None:
            mime_info = magic.from_file(file_path, mime=True) or ''
            file_type = ContentTypesEnum(mime_info.split('/')[0])
        else:
            file_type = ''
        cls = ContentTypesEnum.get_class(file_type)
        file_obj = cls(file_path, file_type)

        # constructing file's new path
        new_path_parts = [self.dst_path]
        for lvl, lvl_tags in self.path_structure:
            lvl = TagProcessor.process_string(
                file_obj=file_obj, string=lvl, tags=lvl_tags)
            new_path_parts.append(lvl)

        new_file_dir = os.path.join(*new_path_parts)

        if not os.path.exists(new_file_dir):
            os.makedirs(new_file_dir)

        # resolving conflict if file already exists
        handler = ConflictResolveMethodEnum.handlers()[
            self.conflict_resolve_method]
        handler(file_path, new_file_dir)

        # doing main job
        handler = SortMethodEnum.handlers()[self.method]
        handler(file_path, new_file_dir)

        # delete empty old folder if needed
        handler = FolderCleanupOptionsEnum.handlers()[self.cleanup_option]
        handler(file_path, new_file_dir)
