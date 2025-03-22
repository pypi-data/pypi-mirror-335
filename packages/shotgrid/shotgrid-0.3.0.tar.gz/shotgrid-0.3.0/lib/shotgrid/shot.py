#!/usr/bin/env python
#
# Copyright (c) 2024, Ryan Galloway (ryan@rsgalloway.com)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  - Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  - Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  - Neither the name of the software nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#

__doc__ = """
Contains Shot base class.
"""

from shotgrid.base import Entity
from shotgrid.logger import log


class Shot(Entity):
    """Shotgrid Shot entity."""

    entity_type = "Shot"

    fields = [
        "id",
        "code",
        "description",
        "assets",
        "sg_sequence",
        "sg_status_list",
        "versions",
    ]

    def __init__(self, *args, **kwargs):
        super(Shot, self).__init__(*args, **kwargs)

    def __repr__(self):
        return '<{0} "{1}">'.format(self.__class__.__name__, self.data.code)

    def create_task(self, content: str, **data):
        """Creates a new Task with this shot as the parent.

        :param content: task name
        :param data: task data dictionary
        :return: new Task object
        """
        from shotgrid.task import Task

        data.update({"content": content, "entity": self.data})
        results = self.create("Task", data=data)
        return Task(self, results)

    def create_version(self, code: str, task: dict, **data):
        """Creates a new Version with this shot as the parent.

        :param code: version name
        :param data: version data dictionary
        :return: new Version object
        """
        from shotgrid.version import Version

        data.update({"code": code, "entity": self.data, "sg_task": task.data})
        results = self.create("Version", data=data)
        return Version(self, results)

    def sequence(self, deep: bool = False):
        """Returns the Sequence object for this Shot.

        If deep is False, returned data is shallow, only containing the
        following fields: id, name, and type.

        :param deep: return default Step fields (default False).
        :return: Sequence object for this Shot.
        :raise: gaierror if can't connect to shotgrid.
        """
        from shotgrid.sequence import Sequence

        seq = Sequence(self.parent(), self.data.sg_sequence)

        if deep:
            seq.refetch()

        return seq
