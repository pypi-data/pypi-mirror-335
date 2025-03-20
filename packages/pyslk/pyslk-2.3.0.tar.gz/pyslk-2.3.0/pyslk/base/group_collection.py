from __future__ import annotations

import json
from typing import Union

from .file_group import FileGroup

__all__ = ["GroupCollection"]


class GroupCollection:
    def __init__(self):
        # dict has structure "index: job"
        # thus, we can have jobs without job id
        self.groups: dict[int, FileGroup] = dict()
        # iterator not initialized
        self.iterator = None

    def __iter__(self):
        self.iterator = iter(self.groups)
        return self

    def __next__(self):
        return self.iterator.__next__()

    def add_group(self, group: Union[FileGroup, dict]) -> int:
        # if group is no RecallJob but a dict, then create RecallJob from the dict
        if isinstance(group, dict):
            group = FileGroup(group)
        # add group to groups dict
        search_id: int = group.get_search_id()
        if search_id not in self.groups:
            # group does not exist yet in groups
            self.groups[search_id] = group
        else:
            # a group with the same search id exists already in groups
            self.groups[search_id] = self.groups[search_id].merge_group(group)
        # return search id of the group
        return search_id

    def get_group(self, search_id: int) -> FileGroup:
        return self.groups.get(search_id, None)

    def dump(self) -> dict[int, dict]:
        return {k: v.dump() for k, v in self.groups.items()}

    def __str__(self) -> str:
        """
        print a JSON string of all jobs in this job collection

        :return: JSON strong of all jobs in this job collection
        :rtype: str
        """
        return json.dumps({k: v.__str__() for k, v in self.groups.items()})

    def json(self) -> str:
        """
        print a JSON string of all jobs in this job collection

        :return: JSON strong of all jobs in this job collection
        :rtype: str
        """
        return self.__str__()

    def __len__(self) -> int:
        return len(self.groups)

    def size(self) -> int:
        return self.__len__()
