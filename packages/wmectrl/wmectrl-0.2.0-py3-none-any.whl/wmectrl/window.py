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

import typing

from gi.repository import Wnck

from .screen import Screen
from .wmectrl import Wmectrl
from .workspace import Workspace


class Window(Wmectrl):
    def __init__(self, screen: Screen):
        super().__init__()
        self.screen = screen
        self.obj = None

    def __str__(self):
        """
        Returns the window information
        """
        return f'{self.get_xid()} {self.get_name()}'

    def activate(self) -> None:
        """
        Activate the window
        """
        self.obj.activate(self.get_timestamp())

    def close(self) -> None:
        """
        Close the window
        """
        self.obj.close(self.get_timestamp())

    def find_window(self,
                    reference: str,
                    exact_title: bool,
                    exact_pid: bool,
                    exact_xid: bool,
                    exact_app_title: bool,
                    exact_app_pid: bool) -> Wnck.Window:
        """
        Find a window by reference

        return: Wnck.Window object
        """
        for window in self.screen.obj.get_windows():
            if exact_title:
                # Search for exact title
                if reference == window.get_name():
                    break
            elif exact_pid:
                # Search for exact PID
                if int(reference) == window.get_pid():
                    break
            elif exact_xid:
                # Search for exact XID
                if int(reference) == window.get_xid():
                    break
            elif exact_app_title:
                # Search for exact application title
                if reference == window.get_application().get_name():
                    break
            elif exact_app_pid:
                # Search for exact application PID
                if reference == window.get_application().get_pid():
                    break
            else:
                # Search for contained title
                if reference in window.get_name():
                    break
        else:
            # Window not found
            window = None
        self.obj = window
        return self.obj

    def get_active(self) -> Wnck.Window:
        """
        Get the active window

        return: Wnck.Window object
        """
        self.obj = self.screen.obj.get_active_window()
        return self.obj

    def get_all_windows(self) -> list['Window']:
        """
        Get list with all the windows
        """
        result = []
        for obj in self.screen.obj.get_windows():
            window = Window(screen=self.screen)
            window.obj = obj
            result.append(window)
        return result

    def get_information(self,
                        workspace: Workspace
                        ) -> dict[str, typing.Union[str, int, bool]]:
        xwindow_geometry = self.obj.get_geometry()
        client_geometry = self.obj.get_client_window_geometry()
        application = self.obj.get_application()
        result = {
            'Screen number': self.screen.obj.get_number(),
            'Screen size': f'{self.screen.obj.get_width()}x'
                           f'{self.screen.obj.get_height()}',
            'WM name': self.screen.obj.get_window_manager_name() or '',
            'Showing desktop': self.screen.obj.get_showing_desktop(),
            'Windows count': len(self.screen.obj.get_windows()),
            'Window name': self.get_name() or '',
            'Window PID': self.get_pid(),
            'Window XID': self.get_xid(),
            'Window position': f'{xwindow_geometry.xp},'
                               f'{xwindow_geometry.yp}',
            'Window size': f'{xwindow_geometry.widthp}x'
                           f'{xwindow_geometry.heightp}',
            'Client position': f'{client_geometry.xp},'
                               f'{client_geometry.yp}',
            'Client size': f'{client_geometry.widthp}x'
                           f'{client_geometry.heightp}',
            'Window is active': self.obj.is_active(),
            'Window is above': self.obj.is_above(),
            'Window is below': self.obj.is_below(),
            'Window is fullscreen': self.obj.is_fullscreen(),
            'Window is minimized': self.obj.is_minimized(),
            'Window is maximized': self.obj.is_maximized(),
            'Window is maximized H': self.obj.is_maximized_horizontally(),
            'Window is maximized V': self.obj.is_maximized_vertically(),
            'Window is pinned': self.obj.is_pinned(),
            'Window is shaded': self.obj.is_shaded(),
            'Window is sticky': self.obj.is_sticky(),
            'Window skip pager': self.obj.is_skip_pager(),
            'Window skip tasklist': self.obj.is_skip_tasklist(),
            'Window in workspace': self.obj.is_on_workspace(workspace.obj),
            'Window in viewport': self.obj.is_in_viewport(workspace.obj),
            'Window needs attention': self.obj.needs_attention(),
            'Application PID': application.get_pid(),
            'Application name': application.get_name() or '',
            'Application startup ID': application.get_startup_id() or '',
            'Workspaces count': self.screen.obj.get_workspace_count(),
            'Workspace number': workspace.obj.get_number(),
            'Workspace name': workspace.obj.get_name() or '',
            'Workspace size': f'{workspace.obj.get_width()}x'
                              f'{workspace.obj.get_height()}',
            'Workspace viewport': f'{workspace.obj.get_viewport_x()}x'
                                  f'{workspace.obj.get_viewport_y()}',
            'Workspace is virtual': workspace.obj.is_virtual(),
        }
        return result

    def get_name(self) -> int:
        """
        Get the window name
        """
        return self.obj.get_name()

    def get_pid(self) -> int:
        """
        Get the window PID
        """
        return self.obj.get_pid()

    def get_xid(self) -> int:
        """
        Get the window X Window ID
        """
        return self.obj.get_xid()

    def manual_move(self) -> None:
        """
        Start window move using keyboard/mouse
        """
        self.obj.keyboard_move()

    def manual_resize(self) -> None:
        """
        Start window resize using keyboard/mouse
        """
        self.obj.keyboard_size()

    def move_to_workspace(self, workspace: Workspace) -> None:
        """
        Move the window to the workspace
        """
        self.obj.move_to_workspace(workspace.obj)

    def set_above(self, status) -> None:
        """
        Set or unset the window above others
        """
        if status:
            self.obj.make_above()
        else:
            self.obj.unmake_above()

    def set_below(self, status) -> None:
        """
        Set or unset the window below others
        """
        if status:
            self.obj.make_below()
        else:
            self.obj.unmake_below()

    def set_fullscreen(self, status) -> None:
        """
        Set or unset the window fullscreen
        """
        if status is not None:
            self.obj.set_fullscreen(status)

    def set_geometry(self,
                     left: int,
                     top: int,
                     width: int,
                     height: int) -> None:
        """
        Move or resize the window
        """
        move_resize_mask = 0
        if left is not None:
            move_resize_mask |= Wnck.WindowMoveResizeMask.X
        if top is not None:
            move_resize_mask |= Wnck.WindowMoveResizeMask.Y
        if width is not None:
            move_resize_mask |= Wnck.WindowMoveResizeMask.WIDTH
        if height is not None:
            move_resize_mask |= Wnck.WindowMoveResizeMask.HEIGHT
        self.obj.set_geometry(Wnck.WindowGravity.STATIC,
                              move_resize_mask,
                              left or 1000,
                              top or 1000,
                              width or 1000,
                              height or 1000)

    def set_minimize(self, status) -> None:
        """
        Set or unset the window minimized
        """
        if status:
            self.obj.minimize()
        else:
            self.obj.unminimize(self.get_timestamp())

    def set_maximize(self, status) -> None:
        """
        Set or unset the window maximized
        """
        if status:
            self.obj.maximize()
        else:
            self.obj.unmaximize()

    def set_maximize_horizontally(self, status) -> None:
        """
        Set or unset the window maximized horizontally
        """
        if status:
            self.obj.maximize_horizontally()
        else:
            self.obj.unmaximize_horizontally()

    def set_maximize_vertically(self, status) -> None:
        """
        Set or unset the window maximized vertically
        """
        if status:
            self.obj.maximize_vertically()
        else:
            self.obj.unmaximize_vertically()

    def set_pin(self, status) -> None:
        """
        Set or unset the window pinned
        """
        if status:
            self.obj.pin()
        else:
            self.obj.unpin()

    def set_shade(self, status) -> None:
        """
        Set or unset the window shaded
        """
        if status:
            self.obj.shade()
        else:
            self.obj.unshade()

    def set_skip_pager(self, status) -> None:
        """
        Set or unset the window skip pager
        """
        self.obj.set_skip_pager(status)

    def set_skip_tasklist(self, status) -> None:
        """
        Set or unset the window skip tasklist
        """
        self.obj.set_skip_tasklist(status)

    def set_sticky(self, status) -> None:
        """
        Set or unset the window sticky
        """
        if status:
            self.obj.stick()
        else:
            self.obj.unstick()
