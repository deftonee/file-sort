import argparse
import os
import sys

from gettext import gettext as _

from enums import (
    SortMethodEnum, ConflictResolveMethodEnum, FolderCleanupOptionsEnum)
from main import Sorter
from tag_classes import get_tag_help

# progress bar constants
PGB_WIDTH = 40
PGB_TEMPLATE = '[%s]'
PGB_ON_CHAR = '#'
PGB_OFF_CHAR = ' '
PGB_FULL_WIDTH = len(PGB_TEMPLATE % (PGB_OFF_CHAR * PGB_WIDTH))

parser = argparse.ArgumentParser(epilog=get_tag_help())

parser.add_argument('src_path', type=str,
                    help=_('Source folder'))
parser.add_argument('dst_path', type=str,
                    help=_('Destination folder'))
parser.add_argument('path_format', type=str,
                    help=_('Folder structure format'))
parser.add_argument("-m", "--move",
                    help=_('Move files instead of copying them'),
                    action="store_true")
parser.add_argument("-r", "--replace",
                    help=_('Replace files with same names'),
                    action="store_true")
parser.add_argument("-n", "--do-nothing",
                    help=_(
                        'Do nothing when file with same name already exists'),
                    action="store_true")
parser.add_argument("-d", "--dispose-folders",
                    help=_('Dispose empty folders'),
                    action="store_true")

args = parser.parse_args()

try:
    if args.move:
        sm = SortMethodEnum.MOVE
    else:
        sm = SortMethodEnum.COPY

    if args.replace:
        crm = ConflictResolveMethodEnum.REPLACE
    elif args.do_nothing:
        crm = ConflictResolveMethodEnum.DO_NOTHING
    else:
        crm = ConflictResolveMethodEnum.SAVE_ALL

    if args.dispose_folders:
        co = FolderCleanupOptionsEnum.REMOVE
    else:
        co = FolderCleanupOptionsEnum.LEAVE

    total = 0
    for x in os.walk(args.src_path):
        total += len(x[2])
    delta = PGB_WIDTH / total

    i = 0.0

    sorter = Sorter(src_path=args.src_path, dst_path=args.dst_path,
                    path_format=args.path_format, method=sm,
                    conflict_resolve_method=crm, cleanup_option=co)
    is_valid, msg = sorter.validate_paths()

    if is_valid:
        for is_done, file_name in sorter.sort():
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
        sys.stdout.write(f'\n[FAIL] {msg}\n')
        sys.stdout.flush()


except KeyboardInterrupt:
    sys.stdout.write('\n[INFO] %s\n' % _('The sorting process is interrupted'))
    sys.stdout.flush()

except ZeroDivisionError:
    sys.stdout.write('\n[INFO] %s\n' % _('No files to sort'))
    sys.stdout.flush()

sys.exit()
