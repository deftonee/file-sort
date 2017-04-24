
import os
import sys

from gettext import gettext as _
from main import validate, sort, SortMethodEnum


PGB_WIDTH = 40
PGB_TEMPLATE = '[%s]'
PGB_ON_CHAR = '#'
PGB_OFF_CHAR = ' '
PGB_FULL_WIDTH = len(PGB_TEMPLATE % (PGB_OFF_CHAR * PGB_WIDTH))

if len(sys.argv) != 4:
    sys.stdout.write('[FAIL] %s\n%s\n' % (
        _('Not enough arguments. Example:'),
        '$ python3 cli.py /home/user/src /home/user/dst %T/%Y/%m-%d'
    ))
    sys.stdout.flush()
    sys.exit()

try:
    src_path = sys.argv[1]
    dst_path = sys.argv[2]
    path_format = sys.argv[3]

    is_valid, msg = validate(src_path, dst_path, path_format,
                             SortMethodEnum.values[SortMethodEnum.COPY])
    if is_valid:

        total = 0
        for x in os.walk(src_path):
            total += len(x[2])
        delta = PGB_WIDTH / total

        i = 0

        for is_done, file_name in sort(
                src_path, dst_path, path_format,
                SortMethodEnum.values[SortMethodEnum.COPY]
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

        sys.stdout.write('\n[INFO] %s\n' % _('Sort process completed'))
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

