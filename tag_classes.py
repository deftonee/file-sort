from gettext import gettext as _

from enums import ContentTypesEnum
from file_classes import File
from helpers import TagProcessor, DEFAULT_FOLDER_NAME


class Tag:
    """ Thing that know how to get information from file by specific tag """
    tag = ''
    help = ''

    @classmethod
    def process(cls, file_obj: File) -> str:
        return ''


class ContentTypeTag(Tag):
    tag = '%T'
    help = _('Content type name of file (Images, Videos, ...)')

    folder_names = {
        ContentTypesEnum.IMAGE: _('Images'),
        ContentTypesEnum.VIDEO: _('Videos'),
        ContentTypesEnum.AUDIO: _('Audios'),
        ContentTypesEnum.TEXT: _('Documents'),
    }

    @classmethod
    def process(cls, file_obj: File) -> str:

        return cls.folder_names.get(
            file_obj.content_type,
            DEFAULT_FOLDER_NAME)


class ExtensionTag(Tag):
    tag = '%E'
    help = _('Extension of file (jpg, png, doc, avi, ...)')

    @classmethod
    def process(cls, file_obj: File) -> str:
        return file_obj.extension


class DateTimeTag(Tag):
    @classmethod
    def process(cls, file_obj: File) -> str:
        return file_obj.date.strftime(cls.tag)


class YearTag(DateTimeTag):
    tag = '%Y'
    help = _('Year with century as a decimal number')


class DecimalMonthTag(DateTimeTag):
    tag = '%m'
    help = _('Month as a decimal number [01,12]')


class DayTag(DateTimeTag):
    tag = '%d'
    help = _('Day of the month as a decimal number [01,31]')


class HourTag(DateTimeTag):
    tag = '%H'
    help = _('Hour (24-hour clock) as a decimal number [00,23]')


class MinuteTag(DateTimeTag):
    tag = '%M'
    help = _('Minute as a decimal number [00,59]')


class SecondTag(DateTimeTag):
    tag = '%S'
    help = _('Second as a decimal number [00,61]')


class TimeZoneTag(DateTimeTag):
    tag = '%z'
    help = _('Time zone offset from UTC')


class WeekDayTag(DateTimeTag):
    tag = '%a'
    help = _("Locale's abbreviated weekday name")


class FullWeekDayTag(DateTimeTag):
    tag = '%A'
    help = _("Locale's full weekday name")


class AbbrMonthTag(DateTimeTag):
    tag = '%b'
    help = _("Locale's abbreviated month name")


class MonthTag(DateTimeTag):
    tag = '%B'
    help = _("Locale's full month name")


class DateTimeReprTag(DateTimeTag):
    tag = '%c'
    help = _("Locale's appropriate date and time representation")


class Hour12Tag(DateTimeTag):
    tag = '%I'
    help = _('Hour (12-hour clock) as a decimal number [01,12]')


class DayPartTag(DateTimeTag):
    tag = '%p'
    help = _("Locale's equivalent of either AM or PM")


class CapitalRomanMonthTag(DateTimeTag):
    tag = '%r'
    help = _("Month as a small roman number [ⅰ,ⅻ]")

    ROMAN_NUMBERS = {
        1: 'Ⅰ', 2: 'Ⅱ', 3: 'Ⅲ', 4: 'Ⅳ',
        5: 'Ⅴ', 6: 'Ⅵ', 7: 'Ⅶ', 8: 'Ⅷ',
        9: 'Ⅸ', 10: 'Ⅹ', 11: 'Ⅺ', 12: 'Ⅻ'
    }

    @classmethod
    def process(cls, file_obj: File) -> str:
        return cls.ROMAN_NUMBERS.get(file_obj.date.month, '')


class SmallRomanMonthTag(DateTimeTag):
    tag = '%R'
    help = _("Month as a capital roman number [Ⅰ,Ⅻ]")

    SMALL_ROMAN_NUMBERS = {
        1: 'ⅰ', 2: 'ⅱ', 3: 'ⅲ', 4: 'ⅳ',
        5: 'ⅴ', 6: 'ⅵ', 7: 'ⅷ', 8: 'ⅷ',
        9: 'ⅸ', 10: 'ⅹ', 11: 'ⅺ', 12: 'ⅻ'
    }

    @classmethod
    def process(cls, file_obj: File) -> str:
        return cls.SMALL_ROMAN_NUMBERS.get(file_obj.date.month, '')


class NumberInCircleMonthTag(DateTimeTag):
    tag = '%C'
    help = _("Month as number in circle [①,⑫]")

    NUMBERS_IN_CIRCLES = {
        1: '①', 2: '②', 3: '③', 4: '④',
        5: '⑤', 6: '⑥', 7: '⑦', 8: '⑧',
        9: '⑨', 10: '⑩', 11: '⑪', 12: '⑫'
    }

    @classmethod
    def process(cls, file_obj: File) -> str:
        return cls.NUMBERS_IN_CIRCLES.get(file_obj.date.month, '')


classes = (
    ContentTypeTag,
    ExtensionTag,
    YearTag,
    DecimalMonthTag,
    DayTag,
    HourTag,
    MinuteTag,
    SecondTag,
    TimeZoneTag,
    WeekDayTag,
    FullWeekDayTag,
    AbbrMonthTag,
    MonthTag,
    DateTimeReprTag,
    Hour12Tag,
    DayPartTag,
    CapitalRomanMonthTag,
    SmallRomanMonthTag,
    NumberInCircleMonthTag,
)

for x in classes:
    TagProcessor.add_tag_class(x)

SEPARATOR_HELP = _('''/  - Folder structure separator''')

EXAMPLE_HELP = _('''Format example: %T/%Y/%m%B - %d
Path example for this format: Images/2017/05May - 02/''')

TAG_HELP = '\n'.join((
    SEPARATOR_HELP,
    '\n',
    *(f'{c.tag} - {c.help}' for c in classes),
    '\n',
    EXAMPLE_HELP,
))

