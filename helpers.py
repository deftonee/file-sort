import locale
import logging
import os
import sys
import traceback

from gettext import bindtextdomain
from typing import Text, Set

from enums import DEFAULT_FOLDER_NAME
from file_classes import File


def set_locale():
    """ Set language for text translation """
    try:
        # TODO maybe use command line tools
        #  like "defaults read -g AppleLanguages"
        code, encoding = locale.getdefaultlocale()
    except ValueError:
        logging.error(traceback.format_exc())
    else:
        old_code, old_encoding = locale.getlocale()
        logging.info(f'Locale was code={old_code}, encoding={old_encoding}')
        logging.info(f'Locale will be code={code}, encoding={encoding}')
        locale_variants = (
            '{}.{}'.format(code, encoding),
            *code.split('_')
        )
        bindtextdomain('messages',
                       os.path.join(os.path.dirname(sys.argv[0]), 'locale'))
        for variant in locale_variants:
            os.environ['LANGUAGE'] = variant
            try:
                locale.setlocale(locale.LC_ALL, variant)
            except locale.Error:
                continue
            else:
                break


class TagProcessor:
    """ Class transforms string with tags into folder name """
    tag_classes = {}

    # TODO move here all path logic from main class
    @classmethod
    def process_string(
            cls, file_obj: File, string: Text, tags: Set[Text]) -> Text:
        result = string
        for tag in tags:
            if tag in cls.tag_classes:
                replacement = cls.tag_classes[tag].process(file_obj)
                result = result.replace(tag, replacement)
            else:
                result = DEFAULT_FOLDER_NAME
                break
        return result

    @classmethod
    def add_tag_class(cls, tag_cls):
        cls.tag_classes[tag_cls.tag] = tag_cls
