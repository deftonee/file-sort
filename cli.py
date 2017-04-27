
import argparse
import os
import sys

from gettext import gettext as _
from main import validate, sort, SortMethodEnum, FORMAT_HELP

PGB_WIDTH = 40
PGB_TEMPLATE = '[%s]'
PGB_ON_CHAR = '#'
PGB_OFF_CHAR = ' '
PGB_FULL_WIDTH = len(PGB_TEMPLATE % (PGB_OFF_CHAR * PGB_WIDTH))

parser = argparse.ArgumentParser(epilog=FORMAT_HELP)

parser.add_argument('src_path', type=str,
                    help=_('Source folder'))
parser.add_argument('dst_path', type=str,
                    help=_('Destination folder'))
parser.add_argument('path_format', type=str,
                    help=_('Folder structure format'))
parser.add_argument("-m", "--move",
                    help=_('Move files instead of copying them'),
                    action="store_true")

args = parser.parse_args()

try:
    is_valid, msg = validate(
        args.src_path,
        args.dst_path,
        args.path_format,
        SortMethodEnum.values[
            SortMethodEnum.MOVE if args.move else SortMethodEnum.COPY
        ]
    )
    if is_valid:

        total = 0
        for x in os.walk(args.src_path):
            total += len(x[2])
        delta = PGB_WIDTH / total

        i = 0

        for is_done, file_name in sort(
                args.src_path,
                args.dst_path,
                args.path_format,
                SortMethodEnum.values[
                    SortMethodEnum.MOVE if args.move else SortMethodEnum.COPY
                ]
        ):
            i += delta

            # erase last line
            sys.stdout.write(''.join((
                '\r',
                ' ' * PGB_FULL_WIDTH,
                '\r',
            )))
            sys.stdout.flush()

            # print file and progressbar
            sys.stdout.write(''.join((
                '[DONE] ' if is_done else '[FAIL] ',
                file_name,
                '\n',
                PGB_TEMPLATE % (
                    PGB_ON_CHAR * int(i)
                ).ljust(PGB_WIDTH, PGB_OFF_CHAR),
            )))
            sys.stdout.flush()

        sys.stdout.write(''.join((
            '\r',
            PGB_TEMPLATE % (PGB_ON_CHAR * PGB_WIDTH),
            '\n[INFO] ',
            _('Sort process completed'),
            '\n',
        )))
        sys.stdout.flush()

    else:
        sys.stdout.write('\n[FAIL] %s\n' % msg)
        sys.stdout.flush()


except KeyboardInterrupt:
    sys.stdout.write('\n[INFO] %s\n' % _('The sorting process is interrupted'))
    sys.stdout.flush()

except ZeroDivisionError:
    sys.stdout.write('\n[INFO] %s\n' % _('No files to sort'))
    sys.stdout.flush()

sys.exit()

