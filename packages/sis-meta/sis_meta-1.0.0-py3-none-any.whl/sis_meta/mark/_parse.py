"""
Parse MARKS_SEGMENT.
"""
import re
import struct

POSITIONS = re.compile(rb'''
POSITIONS; BEGIN; VECTOR_DOUBLE;BINARY;(\d+)
(.+)
POSITIONS; END''', re.DOTALL
)

IDS = re.compile(rb'''
IDS; BEGIN; VECTOR_INT;BINARY;(\d+)
(.+)
IDS; END''', re.DOTALL
)

LENGTHS = re.compile(rb'''
LENGTHS; BEGIN; VECTOR_DOUBLE;BINARY;(\d+)
(.+)
LENGTHS; END''', re.DOTALL
)

TEXTS_LONG = re.compile(rb'''
TEXTS; BEGIN; VECTOR_STRING
(.+)
TEXTS; END
''', re.DOTALL
)

TEXTS_SHORT = re.compile(rb'''
TEXTS; (.+)

TEXT_ATTR_POSITIONS; BEGIN;''', re.DOTALL
)

def parse_marks_segment(raw_data):
    """
    Parse MARKS_SEGMENT.

    Parameters
    ----------
    raw_data : bytes
        The data in a meta file. It MUST contain POSITIONS, IDS, LENGTHS
        and TEXTS tags.

    Returns
    -------
    zip of tuples, [(position, length, text, group_id, group_name), ...]
        A zip of tuples. Each tuple contains the start position,
        length, text, group_id and group_name of a mark.
    """
    # Read positions
    positions_match = POSITIONS.search(raw_data)
    #position_size = positions_match.group(1)
    positions_bytes = positions_match.group(2)[4:]
    positions = struct.unpack(f'{len(positions_bytes) // 8}d', positions_bytes)

    # Read ids / also known as groups
    ids_match = IDS.search(raw_data)
    #ids_size = ids_match.group(1)
    ids_bytes = ids_match.group(2)[4:]
    group_ids = struct.unpack(f'{len(ids_bytes) // 4}i', ids_bytes)

    # Read lengths
    lengths_match = LENGTHS.search(raw_data)
    #lengths_size = lengths_match.group(1)
    lengths_bytes = lengths_match.group(2)[4:]
    lengths = struct.unpack(f'{len(lengths_bytes) // 8}d', lengths_bytes)

    # Read texts
    texts_match = TEXTS_LONG.search(raw_data)
    if texts_match is None:
        texts_match = TEXTS_SHORT.search(raw_data)
    texts_bytes = texts_match.group(1)
    texts = []
    for text_bytes in texts_bytes.split(b';'):
        text_bytes = text_bytes.replace(bytes.fromhex('02'), b'\n') #Start of Text: U+0002
        text_bytes = text_bytes.replace(bytes.fromhex('03'), b';') #End of Text: U+0003
        text_bytes = text_bytes.replace(b'_|!!|_nuse', b'') #End of Text: U+0003
        texts.append(text_bytes.decode())
    return zip(positions, lengths, texts, group_ids)
