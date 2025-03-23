# wmectrl

[![CircleCI Build Status](https://img.shields.io/circleci/project/github/muflone/wmectrl/master.svg)](https://circleci.com/gh/muflone/wmectrl)
[![Python 3.9](https://github.com/muflone/wmectrl/actions/workflows/python-3.9.yml/badge.svg)](https://github.com/muflone/wmectrl/actions/workflows/python-3.9.yml)
[![Python 3.10](https://github.com/muflone/wmectrl/actions/workflows/python-3.10.yml/badge.svg)](https://github.com/muflone/wmectrl/actions/workflows/python-3.10.yml)
[![Python 3.11](https://github.com/muflone/wmectrl/actions/workflows/python-3.11.yml/badge.svg)](https://github.com/muflone/wmectrl/actions/workflows/python-3.11.yml)
[![Python 3.12](https://github.com/muflone/wmectrl/actions/workflows/python-3.12.yml/badge.svg)](https://github.com/muflone/wmectrl/actions/workflows/python-3.12.yml)
[![Python 3.13](https://github.com/muflone/wmectrl/actions/workflows/python-3.13.yml/badge.svg)](https://github.com/muflone/wmectrl/actions/workflows/python-3.13.yml)

**Description:** An enhanced window manager control

**Copyright:** 2010-2025 Fabio Castelli (Muflone) <muflone@muflone.com>

**License:** GPL-3+

**Source code:** https://github.com/muflone/wmectrl/

**Documentation:** http://www.muflone.com/wmectrl/

# Description

**wmectrl** is a command-line tool to control your applications windows by
moving, resize, minimize, maximize, set your windows to full screen and so on.

You can also use **wmectrl** to get some details about a specific window or
the currently active window.

# System Requirements

* Python >= 3.9 (developed and tested for Python 3.13)
* GObject library for Python 3 ( https://pypi.org/project/PyGObject/ )
* GTK+ 3.x library
* Wnck 3.x library

# Usage

wmectrl is a command line utility and requires some arguments to be passed:

```
wmectrl
  -h, --help                    Show this help message and exit
  --version                     Show program's version number and exit

Actions:
  -L, --list-windows            List all windows titles
  -d, --show-desktop            Show the desktop
  -I, --show-information        Show information about selected screen

Selection:
  -w, --window WINDOW           Select window
  -s, --screen SCREEN           Select screen number
  -S, --workspace WORKSPACE     Select workspace number
  --exact-title                 Select window by exact title
  --exact-pid                   Select window by exact PID
  --exact-xid                   Select window by exact XID
  --exact-app-title             Select window by application title
  --exact-app-pid               Select window by application PID

Window control:
  -A, --activate                Activate the selected window
  -C, --close                   Close the selected window
  -P, --pin BOOL                Pin/unpin the window
  -G, --skip-pager BOOL         Set/unset skip pager for the window
  -K, --skip-tasklist BOOL      Set/unset skip tasklist for the window
  -D, --shade BOOL              Shade/unshade the window
  -J, --sticky BOOL             Stick/unstick the window

Window position:
  -E, --above BOOL              Set/unset the window above others
  -B, --below BOOL              Set/unset the window below others
  -T, --move-to                 Move the window to the selected workspace
  -U, --manual-move             Move the window using keyboard/mouse
  -X, --left LEFT               Set left/X position of the window
  -Y, --top TOP                 Set top/Y position of the window

Window size:
  -m, --minimized BOOL          Minimize/unminimize the window
  -M, --maximized BOOL          Maximize/unmaximize the window
  -O, --horizontally BOOL       Maximize/unmaximize horizontally the window
  -V, --vertically BOOL         Maximize/unmaximize vertically the window
  -W, --width WIDTH             Set width of the window
  -H, --height HEIGHT           Set height of the window
  -F, --fullscreen BOOL         Enter/exit fullscreen for the window
  -R, --manual-resize           Start window resize using keyboard/mouse

Workspace control:
  --set-workspaces-count COUNT  Change the number of workspaces
  --set-workspace-name NAME     Change the workspace name
  --set-workspace-active        Change the active workspace
```

Some commands require you to specify a window to act on it (for example to
minimize it). If a window is not specified with the `-w/--window` argument
(see the window selection section below) the currently active window is used
and the other arguments will be used with it.

Using the `--show-information` argument you can obtain details about the
selected window.

```
$ wmectrl --show-information

Screen number          : 0
Screen size            : 3280x1080
WM name                : GNOME Shell
Showing desktop        : False
Windows count          : 10
Window name            : wmectrl – README.md
Window PID             : 223212
Window XID             : 14708260
Window position        : 0,32
Window size            : 1920x1048
Client position        : 0,32
Client size            : 1920x1048
Window is active       : True
Window is above        : False
Window is below        : False
Window is fullscreen   : False
Window is minimized    : False
Window is maximized    : True
Window is maximized H  : True
Window is maximized V  : True
Window is pinned       : False
Window is shaded       : False
Window is sticky       : False
Window skip pager      : False
Window skip tasklist   : False
Window in workspace    : True
Window in viewport     : True
Window needs attention : False
Application PID        : 223212
Application name       : jetbrains-pycharm
Application startup ID : 
Workspaces count       : 6
Workspace number       : 0
Workspace name         : Workspace 1
Workspace size         : 3280x1080
Workspace viewport     : 0x0
Workspace is virtual   : False
```

Many arguments will require you to specify a BOOL value which may be `true` to
enable the command, while `false` is used to disable the command.

# Window selection

When no window is selected using `-w/--window` argument the currently active
window is automatically selected, therefore any window control/position/size
command will act upon that window.

You can specify the needed window in multiple ways, using a partial search
on the window title or an exact match (`--exact-title`) on the window title
or its XWindow ID (`--exact-xid`) or the application name (`--exact-app-title`)
or by using the application Process ID (`--exact-app-pid`).

To obtain some information about the currently visibile windows you can use
the `--list-windows` argument which lists both XID, PID and window title.

```
$ wmectrl --list-windows

XID        PID      Name
0x03200046 7156     Mozilla Thunderbird
0x05200046 224285   Mozilla Firefox
0x00e02428 223212   PixelColor – README.md
0x00e0288f 223212   wmectrl – README.md
```

To get a window by a partial search on its name you can use:

```
$ wmectrl --show-information --window 'PixelColor'
```

This will print all the details for the **first window** having PixelColor on
its title.

To narrow the search for your window you can also specify a full title with
the `--exact-title` argument.

```
$ wmectrl --show-information --window 'PixelColor – README.md' --exact-title
```

You can also specify the exact XWindow ID using `--exact-xid`:

```
$ wmectrl --show-information --window 14708806 --exact-xid
```

At the same way you can specify the process ID using `--exact-pid`, but please
be aware multiple windows can have the same process ID as an application can
open multiple windows:

```
$ wmectrl --show-information --window 223212 --exact-xid
```

If you know the exact application name you can get the window using it with
`--exact-app-title`:

```
$ wmectrl --show-information --window 'jetbrains-pycharm' --exact-app-title
```
