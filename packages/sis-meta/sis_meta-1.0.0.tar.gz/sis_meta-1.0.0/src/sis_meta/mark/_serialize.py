"""
Serialize MARKS_SEGMENT 
"""
import re
from struct import pack
from importlib.resources import files

MAX_BYTES_TEXT_MARK = 1022
MAX_BYTES_ALL_TEXT_MARKS = 3001

MARKS_SEGMENT = re.compile(
    rb'MARKS_SEGMENT; BEGIN;.+?(\n.+)\n\nMARKS_SEGMENT; END', re.DOTALL
)

template_path = files('sis_meta.mark') / 'templates/marks_segment.meta'

def serialize_marks_segment(meta):
    """
    Serialize the marks in a :class:`meta_sis.Meta` object.

    Parameters
    ----------
    meta : :class:`meta_sis.Meta`
        A class for handling Meta files.

    Returns
    -------
    bytes
        The content of MARKS_SEGMENT
    """
    data = {
        'positions': [],
        'lengths': [],
        'texts': [],
        'ids': [],
    }

    for mark in meta:
        data['positions'].append(mark.position)
        data['lengths'].append(mark.length)
        data['ids'].append(mark.group_id)
        data['texts'].append(mark.text)

    meta = build_marks_segment(
        data['positions'],
        data['lengths'],
        data['ids'],
        data['texts']
    )
    return meta

def build_marks_segment(positions, lengths, ids, texts):
    """
    Build the content of MARKS_SEGMENT.

    Parameters
    -----------
    positions : list of float
        The starting point of the guide marks.
    lengths : list of float
        The duration of the guide marks.
    ids : list of int
        The group each guide mark belong to.
    texts : list of str
        The content of the guide marks.

    Returns
    -------
    bytes
        The content of a meta file.

    Notes
    -----
    The parameters must be equal in length. In the other hand, ids are 
    limited to the ones existing in the GROUPS_SEGMENT. By default they are:
        - 2 for `Single`
        - 3 for `Sounds`
        - 4 for `Noises`
        - 6 for `Speakers/M1`
        - 7 for `Speakers/M2`
        - 8 for `Speakers/F1`
        - 9 for `Speakers/F2`
        - 10 for `VAD`
        - 11 for `For_AutoCmp`
        - 13 for `Edit_Tracker/ET_LM`

    TEXT_ATTR_POSITIONS, TEXT_ATTR_LENGTHS, TEXT_ATTR_TYPES and
    TEXT_ATTR_VALUES seem to have the same attributes; so I decided to
    copy the values of TEXT_ATTR_POSITIONS on the other's parts.

    The lists pass as arguments must have the same lenght.
    """
    # Load template
    data = template_path.read_bytes()

    n_items = len(positions)

    # Replace values:
    # MARKS_SEGMENT
    # POSITIONS
    bytes_block = pack(f'=I{n_items}d', n_items, *positions)
    data = _update_meta(data, bytes_block, '{{ positions_size }}', '{{ positions }}')

    # LENGTHS
    bytes_block = pack(f'=I{n_items}d', n_items, *lengths)
    data = _update_meta(data, bytes_block, '{{ lengths_size }}', '{{ lengths }}')

    # IDS
    bytes_block = pack(f'=I{n_items}L', n_items, *ids)
    data = _update_meta(data, bytes_block, '{{ ids_size }}', '{{ ids }}')

    # TEXTS
    bytes_block = _norm_text(texts)
    if n_items < 16:
        bytes_block = b'TEXTS; ' + bytes_block
    else:
        bytes_block = b'TEXTS; BEGIN; VECTOR_STRING\n' + bytes_block + b'\nTEXTS; END'
    data = _update_meta(data, bytes_block, data_tag = '{{ texts }}')

    # TEXT_ATTR_POSITIONS
    zeroes = [0]*n_items
    bytes_block = pack(f'=I{n_items}I', n_items, *zeroes)
    data = _update_meta(data, bytes_block, '{{ attr_size }}', '{{ text_attr_positions }}')

    # TEXT_ATTR_LENGTHS

    # TEXT_ATTR_TYPES

    # TEXT_ATTR_VALUES

    # Calc sizes
    match = MARKS_SEGMENT.match(data)
    data = data.replace(b'{{ marks_segment_size }}', str(len(match.group(1))).encode())

    return data

def _norm_text(text_list):
    """
    Normalize texts in SIS format.

    Parameters
    ----------
    text_list : str
        A list of texts encoded in utf-8.

    Returns
    -------
    bytes
        A block of bytes containing the texts required in SIS format.

    Notes
    -----
    SIS does not allow some characters as texts:
        - Semicolons (``;``) are replaced by ``U+0002``
        - New lines (``\n``) are replaced by ``U+0003``
        - Empty characters (``''``) are replaced by ``_|!!|_nuse``
        - Tabs can be inserted in SIS; However, they are removed when they are
        read again. Characters at the rights are also removed.
        - It seems that each text mark is limited to 1023 bytes.
        - It seems that all text marks are limited to less than 3000 bytes.
    """
    list_ = []
    for text in text_list:
        text = text.encode()
        text = text.replace(b'\n', bytes.fromhex('02')) #Start of Text: U+0002
        text = text.replace(b';', bytes.fromhex('03')) #End of Text: U+0003
        text = text.replace(b'\t', b' ')
        if text == b'':
            text = b'_|!!|_nuse'

        if len(text) > MAX_BYTES_TEXT_MARK:
            text = text[0:MAX_BYTES_TEXT_MARK].decode(errors = 'ignore').encode()
        list_.append(text)

    bytes_block = b';'.join(list_)
    index = 0
    while len(bytes_block) > MAX_BYTES_ALL_TEXT_MARKS:
        index -= 1
        list_[index] = b'1'
        bytes_block = b';'.join(list_)
    return bytes_block

def _update_meta(data, bytes_block, size_tag = None, data_tag = None):
    """
    Update the content of the meta template.

    Parameters
    ----------
    data : bytes
        The content of the meta template.
    bytes_block : bytes
        The new data to be inserted in the tags.
    size_tag : str
        The name of the tag where the size of the data given bytes will be replaced
        with. The size is calculated automatically from the ``byte_blocks`` 
        parameter.
    data_tag : str
        The name of the tag where the ``byte_blocks`` will be replaced with.

    Returns
    -------
    bytes
        A new version of the ``data`` parameter where values in tags are 
        replaced with those in ``byte_blocks``.

    Notes
    -----
    These are the valid tags:
        {{ positions_size }}, {{ positions }}
        {{ ids_size }}, {{ ids }}
        {{ lengths_size }}, {{ lengths }}
        {{ attr_size }}, {{ text_attr_positions }}
    """
    if not size_tag is None:
        data = data.replace(size_tag.encode(), f'{len(bytes_block)}'.encode())
    if not data_tag is None:
        data = data.replace(data_tag.encode(), bytes_block)
    return data
