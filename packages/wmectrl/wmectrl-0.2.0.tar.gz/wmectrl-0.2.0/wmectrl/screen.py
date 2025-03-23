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

from .wmectrl import Wmectrl


class Screen(Wmectrl):
    def __init__(self):
        super().__init__()
        self.obj = None

    def get(self, screen: int) -> Wnck.Screen:
        """
        Get the requested screen

        :param screen: index for the selected screen

        return: Wnck.Screen object
        """
        self.obj = Wnck.Screen.get(screen)
        return self.obj

    def get_default(self) -> Wnck.Screen:
        """
        Get the default screen

        return: Wnck.Screen object
        """
        self.obj = Wnck.Screen.get_default()
        return self.obj

    def show_desktop(self) -> None:
        """
        Show the desktop
        """
        self.obj.toggle_showing_desktop(True)

    def update(self) -> None:
        """
        Update the list of screens
        """
        self.obj.force_update()
