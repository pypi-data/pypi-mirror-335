"""
Read a meta file.
"""
from sis_meta.meta import Meta
from sis_meta.groups import GroupsSegment
from sis_meta.mark import GuideMark
from sis_meta.mark._parse import parse_marks_segment
from sis_meta.regex import META_PATTERN
from sis_meta.io.exceptions import MetaFileError

def read_from_file(path):
    """
    Read a meta file into a :class:`Meta`.

    Parameters
    ----------
    path : str or path-like object
        The path of meta file.

    Returns
    -------
    :class:`sis_meta.Meta`
        An object that contains marks.
    """
    with open(path, 'rb') as raw_file:
        raw_data = raw_file.read()

    match = META_PATTERN.match(raw_data)
    if not match:
        raise MetaFileError(f'Not a Meta File: {path}')

    meta = Meta() # Initialize a meta object

    # GROUPS_SEGMENT
    meta._groups = GroupsSegment(
        match.group('GROUPS_SEGMENT')
    )

    # MARKS_SEGMENT
    marks = parse_marks_segment(
        match.group('MARKS_SEGMENT')
    )
    list_ = []
    for position, length, text, group_id in marks:
        group_name = meta._groups.get_name(group_id)
        list_.append(
            GuideMark(position, length, text, group_id, group_name)
        )
    meta._data = list_
    return meta
