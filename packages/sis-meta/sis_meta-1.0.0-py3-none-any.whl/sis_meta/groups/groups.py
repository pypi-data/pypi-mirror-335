"""
Class for handling GROUPS_SEGMENT in meta file.
"""
import re
import io
from importlib.resources import files

from sis_meta.groups._parse import parse_groups_segment
from sis_meta.groups._serialize import serialize_groups_segment

class GroupsSegment:
    """
    A class for handling GROUPS_SEGMENT.
    """
    def __init__(self, raw_data=None):
        self.data = None

        if raw_data is None:
            path = files('sis_meta.groups.templates') / 'grouptree.meta'
            with open(path, 'rb') as raw_file:
                raw_data = raw_file.read()
                self.data = parse_groups_segment(raw_data)
        else:
            self.data = parse_groups_segment(raw_data)
        self.group_id = self._find_max_id(self.data)

    def __repr__(self):
        return serialize_groups_segment(self.data)

    def _find_max_id(self, data):
        """
        Find the higher ID in GROUPS_SEGMENT.
        """
        for dict_ in data:
            max_value = dict_['id']
            if 'child' in dict_:
                current_value = self._find_max_id(dict_['child'])
                max_value = current_value if current_value > max_value else max_value
        return max_value

    def _find_group(self, data, path):
        """
        Find a GROUP dict.

        Parameters
        ----------
        data : list of dict
            An attribute of the :class:`sis_meta.groups_segment.GroupsSegment`.
        path : list
            list of GROUP items.

        Returns
        -------
        dict or None
            A GROUP dict. If the path does not exist, then return `None`
        """
        group_name = path[0]
        group_name_path = path[1:]

        # Base case
        if len(group_name_path) == 0: # Each element in the path has been consumed
            for dict_ in data:
                if dict_['name'] == group_name:
                    return dict_
            return None

        # Recursive case
        for dict_ in data:
            if not dict_['name'] == group_name:
                continue

            if 'child' in dict_:
                return self._find_group(dict_['child'], group_name_path)

    def _find_group_by_id(self, data, id_):
        """
        Find a GROUP dict.

        Parameters
        ----------
        data : list of dict
            An attribute of the :class:`sis_meta.groups_segment.GroupsSegment`.
        id_ : int
            The group id.

        Returns
        -------
        dict
            A GROUP dict.
        """
        # Base case
        for dict_ in data:
            # Base case
            if dict_['id'] == id_:
                return dict_

            # Recursive case
            if 'child' in dict_:
                result = self._find_group_by_id(dict_['child'], id_)
                if result:
                    return result
        return {}

    @staticmethod
    def _norm_path(path):
        """
        Normalize a GROUP path.

        Parameters
        ----------
        path : str
            The path of a GROUP.

        Returns
        -------
        str
            The normalized path.
        """
        if not path.startswith('All marks'):
            path = 'All marks' if path == '' else f'All marks/{path}'
        return path

    @staticmethod
    def _rgb_to_int(rgb):
        """
        Represent a RGB tuple as a negative integer ranging from -1 to -16777216.

        Parameters
        ----------
        rgb : (int, int, int)
            A 3-tuple representing the RGB color system. The first element
            is for RED, the second is for GREEN and the third is for BLUE.
            Each digit ranges from 0 to 255.

        Returns
        -------
        int
            A negative integer for the given RGB value.

        Examples
        ---------
        >>> rgb_to_meta_color_id(255, 255, 255)
        >>> -1
        >>> rgb_to_meta_color_id(255, 255, 254)
        >>> -2
        >>> rgb_to_meta_color_id(255, 255, 0)
        >>> -256
        >>> rgb_to_meta_color_id(255, 254, 255)
        >>> -257

        Notes
        -----
        Colors in SIS are represented as RGB values in the UI, and as
        negative integers in the meta files.
        """
        global BASE_VALUE 
        global MAX_VALUE
        MAX_VALUE = 255
        BASE_VALUE = 256

        blue = MAX_VALUE - rgb[0]
        green = MAX_VALUE - rgb[1]
        red = MAX_VALUE - rgb[2]
        return -(blue*BASE_VALUE**2 + green*BASE_VALUE + red + 1)

    def get_id(self, path):
        """
        Get the ID of a GROUP.
        """
        path_ = self._norm_path(path).split('/')
        group = self._find_group(self.data, path_)

        if group is None:
            raise GroupNotFoundError(f'Cannot found the GROUP "{path}".')
        return group['id']

    def get_name(self, group_id):
        """
        Get the name of a GROUP.
        """
        group = self._find_group_by_id(self.data, group_id)
        return group.get('name', '')

    def is_path(self, path):
        """
        Check if the GROUP path exists.

        Parameter
        ---------
        path : str
            The path of a GROUP.

        Returns
        -------
        bool
            Return `True` if the GROUP path exists; otherwise, `False`.
        """
        path_list = self._norm_path(path).split('/')
        path_exists = self._find_group(self.data, path_list)

        if path_exists is None:
            return False
        return True

    def insert(self, path, color=None, hotkey=None, userparam=0):
        """
        Insert a GROUP.

        Parameters
        ----------
        path : str
            The path of the GROUP.
        color : (int, int, int) or None, default None
            A tuple representing the color in RGB system.
        hotkey : str or None, default None
            A single ASCII character that works as a shortcut when inserting marks.
            If ``None``, no shortcut is associated with the group.
        userparam : {0, 16, 32, 48}
            A set of values for making visible marks and texts.
            - 0: (visible_marks=True, text_visible=True)
            - 16: (visible_marks=True, text_visible=False)
            - 32: (visible_marks=False, text_visible=True)
            - 48: (visible_marks=False, text_visible=False)

        Examples
        --------
        Insert `MyCats` as a `GROUP`.

        >>> groups_segment = sis_meta.GroupsSegment()
        >>> groups_segment.insert('MyCats')
        
        Then, insert ``Akuma``, ``Kirris``, ``Lala``, ``Gato negro`` and
        ``Gato gordo`` as `SUBGROUPS` of `MyCats`.

        >>> groups_segment.insert('MyCats/Akuma')
        >>> groups_segment.insert('MyCats/Kirris')
        >>> groups_segment.insert('MyCats/Lala', (244, 219, 243), 49, 15)
        >>> groups_segment.insert('MyCats/Gato negro', color = (0, 0, 0))
        >>> groups_segment.insert('MyCats/Gato gordo', hotkey = 'r')
        """
        path_norm = self._norm_path(path)
        parents = path_norm.split('/')[:-1]
        name = path_norm.split('/')[-1]

        group = self._find_group(self.data, parents)

        if group is None:
            raise GroupNotFoundError(f'Cannot found the GROUP "{path}".')

        color_int = 0 if color is None else self._rgb_to_int(color)
        hotkey_int = 0 if hotkey is None else ord(hotkey.upper())

        self.group_id += 1
        dict_ = {
            'id': self.group_id,
            'name': name,
            'color': color_int,
            'hotkey': hotkey_int,
            'userparam': userparam,
        }
        group.setdefault('child', [])
        group['child'].append(dict_)

    def update(self, path, name=None, color=None, hotkey=None, userparam=None):
        """
        Update the attributes of a GROUP.

        path : str
            The path of the GROUP.
        name : str, default `None`
            The new name of the GROUP. If `None`, nothing happens.
        color : (int, int, int) or None, default None
            A tuple representing the color in RGB system.
        hotkey : int, default `None`. If `None`, nothing happens.
            A single ASCII character that works as a shortcut when inserting marks.
        userparam : {0, 16, 32, 48}
            A set of values for making visible marks and texts. See
            :meth:`~sis_meta.groups.GroupsSegment.insert`.
        """
        path = self._norm_path(path)
        path_list = path.split('/')

        group = self._find_group(self.data, path_list)
        if group is None:
            raise GroupNotFoundError(f'Cannot found {path} path.')

        if not name is None:
            group['name'] = name

        if not color is None:
            group['color'] = self._rgb_to_int(color)

        if not hotkey is None:
            group['hotkey'] = ord(hotkey)

        if not userparam is None:
            group['userparam'] = userparam

    def remove(self, path):
        """
        Remove a GROUP.

        Parameters
        ----------
        path : str
            The path of the target GROUP.
        """
        if not self.is_path(path):
            raise GroupNotFoundError(f'Cannot found the GROUP {path}.')

        path_list = self._norm_path(path).split('/')
        group_name = path_list[-1]
        group_path = path_list[:-1]

        group = self._find_group(self.data, group_path)
        subgroups = group['child']

        for index_, dict_ in enumerate(subgroups):
            if dict_['name'] == group_name:
                index = index_
                break
        subgroups.pop(index)

        if len(subgroups) == 0:
            group.pop('child')

class GroupNotFoundError(Exception):
    """
    Class for exception.
    """
