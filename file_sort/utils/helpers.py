import locale
import logging
import os
import sys
import traceback
from gettext import bindtextdomain
from gettext import gettext as _
from typing import Optional, Type

from .enums import LangEnum, MyEnum
from .settings import SettingEnum, Settings

LOCALE_REL_PATH = '../locale'


logger = logging.getLogger(__name__)


def set_locale(predefined: Optional[MyEnum] = None):
    """ Set language for text translation """
    code, encoding = None, None
    if predefined is not None:
        code, encoding = LangEnum.codes()[predefined]
    else:
        try:
            # TODO maybe use command line tools
            #  like "defaults read -g AppleLanguages"
            code, encoding = locale.getdefaultlocale()
        except ValueError:
            logger.error(traceback.format_exc())

    if code is not None:
        old_code, old_encoding = locale.getlocale()
        logger.info(f'Locale was code={old_code}, encoding={old_encoding}')
        logger.info(f'Locale will be code={code}, encoding={encoding}')
        locale_variants = (
            '{}.{}'.format(code, encoding),
            *code.split('_')
        )
        bindtextdomain('messages',
                       os.path.join(os.path.dirname(sys.argv[0]), LOCALE_REL_PATH))
        for variant in locale_variants:
            os.environ['LANGUAGE'] = variant
            try:
                locale.setlocale(locale.LC_ALL, variant)
            except locale.Error:
                continue
            else:
                break


def get_default_folder_name():
    return _('Others')


def save_var_from_enum_to_settings(enum_cls: Type[MyEnum], setting_value: SettingEnum, variable):
    settings = Settings()
    text = variable.get()
    value = enum_cls.to_value(text)
    settings.set(setting_value, value.value)


def load_var_from_enum_to_settings(enum_cls: Type[MyEnum], setting_value: SettingEnum, variable):
    settings = Settings()

    value = settings.get(setting_value)
    if value:
        text = enum_cls.to_text(enum_cls(value))
        variable.set(text)
