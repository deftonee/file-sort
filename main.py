import locale
import os
import re
import shutil
import sys

from typing import Tuple, Iterator, Text, List, Set
from gettext import gettext as _, bindtextdomain

from enums import SME, FCE, CRE, CTE
from tag_processor import TagProcessor

try:
    import magic
except ImportError:
    magic = None

# settings for translation
code, encoding = locale.getdefaultlocale()
locale_variants = (
    f'{code}.{encoding}',
    *code.split('_')
)
bindtextdomain('messages', os.path.join(os.path.dirname(sys.argv[0]), 'locale'))
for variant in locale_variants:
    os.environ['LANGUAGE'] = variant
    try:
        locale.setlocale(locale.LC_ALL, variant)
    except locale.Error:
        continue
    else:
        break

# constants
PATH_DELIMITER = '/'
TAG_PATTERN = '%[a-zA-Z]'


def sort(
        src_path: str,
        dst_path: str,
        path_format: str,
        method: SME,
        conflict_resolve_method: CRE,
        cleanup_option: FCE
) -> Iterator[Tuple[bool, str]]:
    """
    Sort files from src_path and place them in dst_path according to path_format
    """
    path_structure: List[Tuple[Text, Set[Text]]] = []

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

        # defining type of file
        if magic is not None:
            mime_info = magic.from_file(file_path, mime=True) or ''
            file_type = CTE(mime_info.split('/')[0])
        else:
            file_type = ''
        cls = CTE.get_class(file_type)
        file_obj = cls(file_path, file_type)

        # constructing file's new path
        new_path_parts = [dst_path]
        for lvl, lvl_tags in path_structure:
            lvl = TagProcessor.process_string(
                file_obj=file_obj, string=lvl, tags=lvl_tags)
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
        if method == SME.COPY:
            shutil.copy2(file_path, new_file_dir)
        elif method == SME.MOVE:
            shutil.move(file_path, new_file_dir, shutil.copy2)

        # delete empty old folder if needed
        if cleanup_option == FCE.REMOVE:
            old_file_dir = os.path.dirname(file_path)
            if not os.listdir(old_file_dir):
                os.rmdir(old_file_dir)

    for part in path_format.split(PATH_DELIMITER):
        path_structure.append((part, set(re.findall(TAG_PATTERN, part))))

    for result in process_folder(src_path):
        yield result


def validate_paths(src_path: str, dst_path: str) -> Tuple[bool, str]:
    """ check all input parameters """
    if not os.path.isdir(src_path):
        return False, _('Source folder path is not valid')
    if not os.path.isdir(dst_path):
        return False, _('Destination folder path is not valid')

    return True, ''
