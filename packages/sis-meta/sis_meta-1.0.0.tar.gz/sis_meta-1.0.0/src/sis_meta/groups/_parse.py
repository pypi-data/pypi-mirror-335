"""
Parse GROUPS_SEGMENT into a list of dict. 
"""
import re
import io

GROUP = re.compile(rb'''ID; (?P<id>\d+)

NAME; (?P<name>.+)

COLOR; (?P<color>-{0,1}\d+)

HOTKEY; (?P<hotkey>\d+)

USERPARAM; (?P<userparam>\d+)

'''
)
GROUP_OPEN = re.compile(rb'GROUP(\d+); BEGIN; COMPOSITE;BINARY;(\d+)\n')
#GROUP_CLOSE = re.compile(rb'GROUP\d; END')
SUBGROUP_OPEN = re.compile(rb'SUBGROUPS; BEGIN; COMPOSITE;BINARY;\d+\n')
SUBGROUP_CLOSE = re.compile(rb'SUBGROUPS; END\n')

def parse_groups_segment(raw_data):
    """
    Discover group tree structure recursively.

    Parameters
    ----------
    raw_data : bytes
        The GROUPS_SEGMENT data in meta files.

    Returns
    -------
    list of dict
        Returns the GROUPS_SEGMENT in structured way.
    """
    data = io.BytesIO(raw_data)
    return discover_grouptree(data, [])

def discover_grouptree(data, tree):
    """
    Discover group tree structure recursively.

    Parameters
    ----------
    data : :class:`io.BytesIO`
        Binary stream containing the GROUPS_SEGMENT data in meta files.
    tree : list
        It contains the mark groups info.

    Returns
    -------
    list of dict
        Returns the GROUPS_SEGMENT info.
    """
    while True:
        current_position = data.tell()
        line = data.readline()

        # Base case
        if line == b'': # When riching the end of the document
            break

        if GROUP_OPEN.match(line):
            current_position = data.tell()
            data_temp = data.read()

            if GROUP.match(data_temp):
                group_content = GROUP.match(data_temp)
                dict_ = {
                    'id': int(group_content.group('id').decode()),
                    'name': group_content.group('name').decode(),
                    'color': group_content.group('color').decode(),
                    'hotkey': group_content.group('hotkey').decode(),
                    'userparam': group_content.group('userparam').decode(),
                }
                tree.append(dict_)
                current_position+= len(group_content.group(0))
            data.seek(current_position)

        # Recursive condition
        elif SUBGROUP_OPEN.match(line):
            tree[-1]['child'] = discover_grouptree(data, [])

        elif SUBGROUP_CLOSE.match(line):
            break

    return tree
