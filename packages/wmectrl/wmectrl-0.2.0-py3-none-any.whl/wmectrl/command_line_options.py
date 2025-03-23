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

import argparse
import logging

from .constants import APP_NAME, APP_VERSION, APP_DESCRIPTION, TRUE_FALSE


class CommandLineOptions(object):
    """
    Parse command line arguments
    """
    def __init__(self):
        self.options = None
        self.parser = argparse.ArgumentParser(prog=f'{APP_NAME}',
                                              description=APP_DESCRIPTION)
        self.parser.set_defaults(verbose_level=logging.INFO)
        self.parser.add_argument('--version',
                                 action='version',
                                 version=f'{APP_NAME} v{APP_VERSION}')

    def add_group(self, name: str) -> argparse._ArgumentGroup:
        """
        Add a command-line arguments group

        :param name: name for the new group
        :return: _ArgumentGroup object with the new command-line options group
        """
        return self.parser.add_argument_group(name)

    def add_configuration_actions(self) -> None:
        """
        Add actions command-line arguments
        """
        group = self.add_group('Actions')
        group.add_argument('-L',
                           '--list-windows',
                           action='store_true',
                           help='List all windows titles')
        group.add_argument('-d',
                           '--show-desktop',
                           action='store_true',
                           help='Show the desktop')
        group.add_argument('-I',
                           '--show-information',
                           action='store_true',
                           help='Show information about selected screen')

    def add_configuration_selection(self) -> None:
        """
        Add selection command-line arguments
        """
        group = self.add_group('Selection')
        group.add_argument('-w',
                           '--window',
                           action='store',
                           type=str,
                           help='Select window')
        group.add_argument('-s',
                           '--screen',
                           action='store',
                           type=int,
                           help='Select screen number')
        group.add_argument('-S',
                           '--workspace',
                           action='store',
                           type=int,
                           help='Select workspace number')
        group.add_argument('--exact-title',
                           action='store_true',
                           help='Select window by exact title')
        group.add_argument('--exact-pid',
                           action='store_true',
                           help='Select window by exact PID')
        group.add_argument('--exact-xid',
                           action='store_true',
                           help='Select window by exact XID')
        group.add_argument('--exact-app-title',
                           action='store_true',
                           help='Select window by application title')
        group.add_argument('--exact-app-pid',
                           action='store_true',
                           help='Select window by application PID')

    def add_configuration_window(self) -> None:
        """
        Add window command-line arguments
        """
        group = self.add_group('Window control')
        group.add_argument('-A',
                           '--activate',
                           action='store_true',
                           help='Activate the selected window')
        group.add_argument('-C',
                           '--close',
                           action='store_true',
                           help='Close the selected window')
        group.add_argument('-P',
                           '--pin',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Pin/unpin the window')
        group.add_argument('-G',
                           '--skip-pager',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Set/unset skip pager for the window')
        group.add_argument('-K',
                           '--skip-tasklist',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Set/unset skip tasklist for the window')
        group.add_argument('-D',
                           '--shade',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Shade/unshade the window')
        group.add_argument('-J',
                           '--sticky',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Stick/unstick the window')

    def add_configuration_window_position(self) -> None:
        """
        Add window position command-line arguments
        """
        group = self.add_group('Window position')
        group.add_argument('-E',
                           '--above',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Set/unset the window above others')
        group.add_argument('-B',
                           '--below',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Set/unset the window below others')
        group.add_argument('-T',
                           '--move-to',
                           action='store_true',
                           help='Move the window to the selected workspace')
        group.add_argument('-U',
                           '--manual-move',
                           action='store_true',
                           help='Move the window using keyboard/mouse')
        group.add_argument('-X',
                           '--left',
                           action='store',
                           type=int,
                           help='Set left/X position of the window')
        group.add_argument('-Y',
                           '--top',
                           action='store',
                           type=int,
                           help='Set top/Y position of the window')

    def add_configuration_window_size(self) -> None:
        """
        Add window size command-line arguments
        """
        group = self.add_group('Window size')
        group.add_argument('-m',
                           '--minimized',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Minimize/unminimize the window')
        group.add_argument('-M',
                           '--maximized',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Maximize/unmaximize the window')
        group.add_argument('-O',
                           '--horizontally',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Maximize/unmaximize horizontally the window')
        group.add_argument('-V',
                           '--vertically',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Maximize/unmaximize vertically the window')
        group.add_argument('-W',
                           '--width',
                           action='store',
                           type=int,
                           help='Set width of the window')
        group.add_argument('-H',
                           '--height',
                           action='store',
                           type=int,
                           help='Set height of the window')
        group.add_argument('-F',
                           '--fullscreen',
                           action='store',
                           choices=TRUE_FALSE,
                           help='Enter/exit fullscreen for the window')
        group.add_argument('-R',
                           '--manual-resize',
                           action='store_true',
                           help='Start window resize using keyboard/mouse')

    def add_configuration_workspace(self) -> None:
        """
        Add workspace command-line arguments
        """
        group = self.add_group('Workspace control')
        group.add_argument('--set-workspaces-count',
                           action='store',
                           type=int,
                           help='Change the number of workspaces')
        group.add_argument('--set-workspace-name',
                           action='store',
                           type=str,
                           help='Change the workspace name')
        group.add_argument('--set-workspace-active',
                           action='store_true',
                           help='Change the active workspace')

    def parse_options(self) -> argparse.Namespace:
        """
        Parse command-line options

        :return: command-line options
        """
        self.options = self.parser.parse_args()
        # Check for missing options
        if not any(vars(self.options).values()):
            self.parser.print_help()
            self.parser.exit(1)
        return self.options
