"""
Serialize MARKS_GROUPS_DATA 
"""
from importlib.resources import files
import re

from sis_meta.mark._serialize import serialize_marks_segment
from sis_meta.io.exceptions import MetaFileError

MARKS_GROUPS_DATA = re.compile(
rb'''MARKS_GROUPS_DATA; BEGIN; COMPOSITE;BINARY;{{ TOTAL_SIZE }}(
VERSION; 2
.+
)

MARKS_GROUPS_DATA; END''', re.DOTALL
)

template_path = files('sis_meta.io') / 'templates/base.meta'

def write_meta(meta, path):
    """
    Write a :class:`sis_meta.Meta` object as a meta file.

    Parameters
    ----------
    meta : :class:`sis_meta.Meta`
        A :class:`sis_meta.Meta` object.
    path : path-like
        The path of the meta file.
    """
    if len(meta) == 0:
        raise MetaFileError('Cannot write a Meta object without marks!')

    content = serialize_marks_groups_data(meta)
    with open(path, 'wb') as meta_file:
        meta_file.write(content)

def serialize_marks_groups_data(meta):
    """
    Serialize a :class:`sis_meta.Meta` object.
    """
    groups_segment_bytes = str(meta._groups).encode()
    marks_segment_bytes = serialize_marks_segment(meta)

    with open(template_path, 'rb') as meta_file:
        content = meta_file.read()
        content = content.replace(b'{{ GROUPS_SEGMENT }}', groups_segment_bytes)
        content = content.replace(b'{{ MARKS_SEGMENT }}', marks_segment_bytes)
        match = MARKS_GROUPS_DATA.match(content)
        if match:
            size = str(len(match.group(1))).encode()
            content = content.replace(b'{{ TOTAL_SIZE }}', size)
    return content
