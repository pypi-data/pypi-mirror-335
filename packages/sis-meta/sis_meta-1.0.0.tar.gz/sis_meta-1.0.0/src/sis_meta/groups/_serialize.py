"""
Serialize GROUPS_SEGMENT.
"""
import re
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape

env = Environment(
    loader = PackageLoader("sis_meta.groups"),
    autoescape = select_autoescape()
)
env.trim_blocks = True
env.lstrip_blocks  = True
content_template = env.get_template('group.meta')
header_template = env.get_template('group_header.meta')

GROUP = re.compile(r'''GROUP\d+; BEGIN; COMPOSITE;BINARY;(
ID; \d+

NAME; .+

COLOR; -{0,1}\d+

HOTKEY; \d+

USERPARAM; \d+
)

GROUP\d+; END
'''
)

SUBGROUPS = re.compile(
r'''GROUP\d+; BEGIN; COMPOSITE;BINARY;
(.+
SUBGROUPS; BEGIN; COMPOSITE;BINARY;
(.+\n)
SUBGROUPS; END\n
)
GROUP\d+; END
''', re.DOTALL
)

GROUPS_SEGMENT = re.compile(
r'''GROUPS_SEGMENT; BEGIN; COMPOSITE;BINARY;
(.+\n)
GROUPS_SEGMENT; END''', re.DOTALL
)

def _serialize_groups_segment_content(data):
    """
    Serialize GROUPS_SEGMENT.

    Parameters
    ----------
    data : list of dict
        :class:`sis_meta.GroupsSegment`
    """
    group_str = ''
    for dict_ in data:
        child = dict_.get('child')
        group_size = None
        subgroup_size = None
        if child is None:
            temp_text = content_template.render(group = dict_)
            match = GROUP.match(temp_text)
            if match:
                group_size = len(match.group(1).encode())
            group_str += content_template.render(group= dict_, size= group_size)
        else:
            subgroup = _serialize_groups_segment_content(child)
            text = content_template.render(group = dict_, subgroup = subgroup)
            match = SUBGROUPS.match(text)
            if match:
                group_size = len(match.group(1).encode())
                subgroup_size = len(match.group(2).encode())
                group_size += len(str(subgroup_size).encode())

            subgroup_str = content_template.render(
                group = dict_,
                size = group_size,
                subgroup = subgroup,
                subgroup_size = subgroup_size
            )

            group_str += subgroup_str
    return group_str

def serialize_groups_segment(data):
    """
    Serialize GROUPS_SEGMENT.

    Parameters
    ----------
    data : list of dict
        :class:`sis_meta.GroupsSegment`
    """
    content = _serialize_groups_segment_content(data)
    text = header_template.render(content = content)
    match = GROUPS_SEGMENT.match(text)
    if match:
        groups_segment_size = len(match.group(1).encode())
    return header_template.render(content = content, size= groups_segment_size)
