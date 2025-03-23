#!/usr/bin/env python3
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

from .command_line_options import CommandLineOptions
from .constants import TRUE
from . import requires                                            # noqa: F401
from .screen import Screen
from .window import Window
from .workspace import Workspace


def main():
    # Get command-line options
    command_line = CommandLineOptions()
    command_line.add_configuration_actions()
    command_line.add_configuration_selection()
    command_line.add_configuration_window()
    command_line.add_configuration_window_position()
    command_line.add_configuration_window_size()
    command_line.add_configuration_workspace()
    options = command_line.parse_options()
    # Check screen argument
    screen = Screen()
    if options.screen is None:
        if screen.get_default() is None:
            command_line.parser.error(
                message='Default screen not found')
    else:
        if screen.get(screen=options.screen) is None:
            command_line.parser.error(
                message=f'Invalid screen number: {options.screen}')
    # Update workspaces/windows list
    screen.update()
    if options.list_windows:
        # List all the windows
        print('XID        PID      Name')
        for window in Window(screen=screen).get_all_windows():
            print(f'0x{window.get_xid():08x} '
                  f'{window.get_pid():<8d} '
                  f'{window.get_name()}')
    # Show desktop action
    if options.show_desktop:
        screen.show_desktop()
    # Check workspace argument
    workspace = Workspace(screen=screen)
    if options.workspace is None:
        if workspace.get_active() is None:
            command_line.parser.error(message='Active workspace not found')
    else:
        if workspace.get(workspace=options.workspace) is None:
            command_line.parser.error(
                message=f'Invalid workspace number {options.workspace}')
    # Change workspaces count
    if options.set_workspaces_count is not None:
        workspace.set_count(count=options.set_workspaces_count)
    # Change workspace name
    if options.set_workspace_name is not None:
        workspace.set_name(name=options.set_workspace_name)
    # Change active workspace
    if options.set_workspace_active:
        workspace.activate()
    # Select active or specified window
    window = Window(screen=screen)
    if options.window is None:
        # Use active window
        if window.get_active() is None:
            command_line.parser.error(message='Active window not found')
    else:
        # Find a window
        if window.find_window(
                reference=options.window,
                exact_title=options.exact_title,
                exact_pid=options.exact_pid,
                exact_xid=options.exact_xid,
                exact_app_title=options.exact_app_title,
                exact_app_pid=options.exact_app_pid) is None:
            command_line.parser.error(
                message=f'Window not found: {options.window}')
    # Move the window to the workspace
    if options.move_to:
        window.move_to_workspace(workspace=workspace)
    # Set or unset the window above others
    if options.above is not None:
        window.set_above(status=options.above == TRUE)
    # Set or unset the window below others
    if options.below is not None:
        window.set_below(status=options.below == TRUE)
    # Set or unset the window maximized horizontally
    if options.horizontally is not None:
        window.set_maximize_horizontally(status=options.horizontally == TRUE)
    # Set or unset the window maximized vertically
    if options.vertically is not None:
        window.set_maximize_vertically(status=options.vertically == TRUE)
    # Set or unset the window minimized
    if options.minimized is not None:
        window.set_minimize(status=options.minimized == TRUE)
    # Set or unset the window maximized
    if options.maximized is not None:
        window.set_maximize(status=options.maximized == TRUE)
    # Set or unset the window pinned
    if options.pin is not None:
        window.set_pin(status=options.pin == TRUE)
    # Set or unset the window shaded
    if options.shade is not None:
        window.set_shade(status=options.shade == TRUE)
    # Set or unset the window sticky
    if options.sticky is not None:
        window.set_sticky(status=options.sticky == TRUE)
    # Set or unset the window fullscreen
    if options.fullscreen is not None:
        window.set_fullscreen(status=options.fullscreen == TRUE)
    # Set or unset the window skip pager
    if options.skip_pager is not None:
        window.set_skip_pager(status=options.skip_pager == TRUE)
    # Set or unset the window skip tasklist
    if options.skip_tasklist is not None:
        window.set_skip_tasklist(status=options.skip_tasklist == TRUE)
    # Activate the window
    if options.activate:
        window.activate()
    # Start window move using keyboard/mouse
    if options.manual_move:
        window.manual_move()
    # Start window resize using keyboard/mouse
    if options.manual_resize:
        window.manual_resize()
    # Move or resize the window
    if (options.left is not None or
            options.top is not None or
            options.width is not None or
            options.height is not None):
        window.set_geometry(left=options.left,
                            top=options.top,
                            width=options.width,
                            height=options.height)
    # Show information
    if options.show_information:
        window_information = window.get_information(workspace=workspace)
        max_key_length = max([len(key) for key in window_information])
        for key, value in window_information.items():
            print(f'{key:<{max_key_length}} : {value}')
    # Close the window
    if options.close:
        window.close()


if __name__ == '__main__':
    main()
