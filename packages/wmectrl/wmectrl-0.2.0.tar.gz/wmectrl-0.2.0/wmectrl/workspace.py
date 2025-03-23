##
#     Project: wmectrl
# Description: An enhanced window manager control
#      Author: Fabio Castelli (Muflone) <muflone@muflone.com>
#   Copyright: 2010-2025 Fabio Castelli
#     License: GPL-3+
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
##

from gi.repository import Wnck

from .screen import Screen
from .wmectrl import Wmectrl


class Workspace(Wmectrl):
    def __init__(self, screen: Screen):
        super().__init__()
        self.screen = screen
        self.obj = None

    def activate(self) -> None:
        """
        Set the workspace as active
        """
        self.obj.activate(self.get_timestamp())

    def get(self, workspace: int) -> Wnck.Workspace:
        """
        Get the requested workspace

        :param workspace: index for the selected workspace

        return: Wnck.Workspace object
        """
        self.obj = self.screen.obj.get_workspace(workspace)
        return self.obj

    def get_active(self) -> Wnck.Workspace:
        """
        Get the default workspace

        return: Wnck.Workspace object
        """
        self.obj = self.screen.obj.get_active_workspace()
        return self.obj

    def set_count(self, count: int) -> None:
        """
        Change the workspaces number
        """
        self.screen.change_workspace_count(count)

    def set_name(self, name: str) -> None:
        """
        Change the workspace name
        """
        self.obj.change_name(name)
