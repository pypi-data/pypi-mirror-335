"""
Handle annotation files (.meta).
"""
from sis_meta.groups import GroupsSegment
from sis_meta.mark import GuideMark
from sis_meta.io.write_meta import write_meta

class Meta:
    """
    Class for handling guide marks.
    """
    def __init__(self):
        self._data = []
        self._groups = GroupsSegment()

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def _sort(self):
        self._data = sorted(self._data, key=lambda x: x.position)

    def insert_group(self, group_path, *args, **kwargs):
        """
        Insert a new group.

        Parameters
        ----------
        group_path : str
            The path of the group.
        **args : tuple
            These parameters will be passed to 
            :meth:`~sis_meta.groups.GroupsSegment.insert`
        **kwargs : dict
            These parameters will be passed to 
            :meth:`~sis_meta.groups.GroupsSegment.insert`
        """
        self._groups.insert(group_path, *args, **kwargs)

    def update_group(self, group_path, new_name=None, **kwargs):
        """
        Update the attributes in a group.

        Parameters
        ----------
        group_path : str
            The path of the group.
        name : str or None, default None.
            The new name of the group.
        **kwargs : dict
            These parameters will be passed to 
            :meth:`~sis_meta.groups.GroupsSegment.update`
        """
        self._groups.update(group_path, new_name, **kwargs)
        if not new_name is None:
            # Update guide marks
            group_name = group_path.split('/')[-1]
            for mark in self:
                if not mark.group_name == group_name:
                    continue
                mark.group_name = new_name

    def remove_group(self, group_path):
        """
        Remove a group and the guide marks associated with it.

        Parameters
        ----------
        group_path : str
            The path of the group.
        """
        self._groups.remove(group_path)
        group_name = group_path.split('/')[-1]
        self._data = [mark for mark in self if not mark.group_name == group_name]

    def insert_guide_mark(self, group_name, position, length=0, text=''):
        """
        Insert a guide mark.
        """
        mark_group_id = self._groups.get_id(group_name)
        mark_group_name = group_name.split('/')[-1]
        guide_mark = GuideMark(
            position, length, text, mark_group_id, mark_group_name
        )
        self._data.append(guide_mark)
        self._sort()

    def write(self, path):
        """
        Write a meta file.
        """
        write_meta(self, path)
