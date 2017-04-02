# coding: utf-8

import logging

from main import validate, sort

src_path = sys.argv[1]
dst_path = sys.argv[2]
path_format = sys.argv[3]

# src_path = u'/Users/deftone/src'
# dst_path = u'/Users/deftone/dst'
# path_format = u'%T/%Y/%m-%B.%d'


is_valid, msg = validate(src_path, dst_path, path_format)
if is_valid:
    sort(src_path, dst_path, path_format)
else:
    logging.error(msg=msg)
