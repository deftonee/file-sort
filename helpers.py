import locale
import logging
import os
import sys
import traceback

from gettext import bindtextdomain


def set_locale():
    """ Set language for text translation """
    try:
        # TODO maybe use command line tool "defaults read -g AppleLanguages"
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
