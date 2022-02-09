# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Dynamically construct wxPython Menus or MenuBars from a supplied string
    description of the menu.

Menu Description Syntax::

    submenu_label {help_string}
        menuitem_label | accelerator {help_string} [~/-name]: code

*submenu_label*
    Label of a sub menu
*menuitem_label*
    Label of a menu item
{*help_string*}
    Help string to display on the status line (optional)
*accelerator*
    Accelerator key (e.g., Ctrl-C) (The '|' and keyname are optional, but must
    be used together.)
[~]
    The menu item is checkable, but is not checked initially (optional)
[/]
    The menu item is checkable, and is checked initially (optional)
[-]
    The menu item disabled initially (optional)
[*name*]
    Symbolic name used to refer to menu item (optional)
*code*
    Python code invoked when menu item is selected

A line beginning with a hyphen (-) is interpreted as a menu separator.
"""

# =========================================================================
#  Imports:
# =========================================================================


import re
import logging


import wx


logger = logging.getLogger(__name__)


# =========================================================================
#  Constants:
# =========================================================================

help_pat = re.compile(r"(.*){(.*)}(.*)")
options_pat = re.compile(r"(.*)\[(.*)\](.*)")

# Mapping of key name strings to wxPython key codes
key_map = {
    "F1": wx.WXK_F1,
    "F2": wx.WXK_F2,
    "F3": wx.WXK_F3,
    "F4": wx.WXK_F4,
    "F5": wx.WXK_F5,
    "F6": wx.WXK_F6,
    "F7": wx.WXK_F7,
    "F8": wx.WXK_F8,
    "F9": wx.WXK_F9,
    "F10": wx.WXK_F10,
    "F11": wx.WXK_F11,
    "F12": wx.WXK_F12,
}


class MakeMenu:
    """Manages creation of menus."""

    #: Initialize the globally unique menu ID:
    cur_id = 1000

    def __init__(self, desc, owner, popup=False, window=None):
        """Initializes the object."""
        self.owner = owner
        if window is None:
            window = owner
        self.window = window
        self.indirect = getattr(owner, "call_menu", None)
        self.names = {}
        self.desc = desc.split("\n")
        self.index = 0
        self.keys = []
        if popup:
            self.menu = menu = wx.Menu()
            self.parse(menu, -1)
        else:
            self.menu = menu = wx.MenuBar()
            self.parse(menu, -1)
            window.SetMenuBar(menu)
            if len(self.keys) > 0:
                window.SetAcceleratorTable(wx.AcceleratorTable(self.keys))

    def parse(self, menu, indent):
        """Recursively parses menu items from the description."""

        while True:

            # Make sure we have not reached the end of the menu description
            # yet:
            if self.index >= len(self.desc):
                return

            # Get the next menu description line and check its indentation:
            dline = self.desc[self.index]
            line = dline.lstrip()
            indented = len(dline) - len(line)
            if indented <= indent:
                return

            # Indicate that the current line has been processed:
            self.index += 1

            # Check for a blank or comment line:
            if (line == "") or (line[0:1] == "#"):
                continue

            # Check for a menu separator:
            if line[0:1] == "-":
                menu.AppendSeparator()
                continue

            # Allocate a new menu ID:
            MakeMenu.cur_id += 1
            cur_id = MakeMenu.cur_id

            # Extract the help string (if any):
            help = ""
            match = help_pat.search(line)
            if match:
                help = " " + match.group(2).strip()
                line = match.group(1) + match.group(3)

            # Check for a menu item:
            col = line.find(":")
            if col >= 0:
                handler = line[col + 1 :].strip()
                if handler != "":
                    if self.indirect:
                        self.indirect(cur_id, handler)
                        handler = self.indirect
                    else:
                        try:
                            _locl = dict(self=self)
                            exec(
                                "def handler(event, self=self.owner):\n %s\n"
                                % handler,
                                globals(),
                                _locl,
                            )
                            handler = _locl["handler"]
                        except Exception:
                            logger.exception(
                                "Invalid menu handler {:r}".format(handler)
                            )
                            handler = null_handler
                else:
                    try:
                        _locl = dict(self=self)
                        exec(
                            "def handler(event, self=self.owner):\n%s\n"
                            % (self.get_body(indented),),
                            globals(),
                            _locl,
                        )
                        handler = _locl["handler"]
                    except Exception:
                        logger.exception(
                            "Invalid menu handler {:r}".format(handler)
                        )
                        handler = null_handler
                self.window.Bind(wx.EVT_MENU, handler, id=cur_id)
                not_checked = checked = disabled = False
                line = line[:col]
                match = options_pat.search(line)
                if match:
                    line = match.group(1) + match.group(3)
                    not_checked, checked, disabled, name = option_check(
                        "~/-", match.group(2).strip()
                    )
                    if name != "":
                        self.names[name] = cur_id
                        setattr(self.owner, name, MakeMenuItem(self, cur_id))
                label = line.strip()
                col = label.find("|")
                if col >= 0:
                    key = label[col + 1 :].strip()
                    label = "%s%s%s" % (label[:col].strip(), "\t", key)
                    key = key.upper()
                    flag = wx.ACCEL_NORMAL
                    col = key.find("-")
                    if col >= 0:
                        flag = {
                            "CTRL": wx.ACCEL_CTRL,
                            "SHIFT": wx.ACCEL_SHIFT,
                            "ALT": wx.ACCEL_ALT,
                        }.get(key[:col].strip(), wx.ACCEL_CTRL)
                        key = key[col + 1 :].strip()
                    code = key_map.get(key, None)
                    try:
                        if code is None:
                            code = ord(key)
                        self.keys.append(
                            wx.AcceleratorEntry(flag, code, cur_id)
                        )
                    except:
                        pass
                menu.Append(cur_id, label, help, not_checked or checked)
                if checked:
                    menu.Check(cur_id, True)
                if disabled:
                    menu.Enable(cur_id, False)
                continue

            # Else must be the start of a sub menu:
            submenu = wx.Menu()
            label = line.strip()

            # Recursively parse the sub-menu:
            self.parse(submenu, indented)

            # Add the menu to its parent:
            try:
                menu.AppendMenu(cur_id, label, submenu, help)
            except:
                # Handle the case where 'menu' is really a 'MenuBar' (which does
                # not understand 'MenuAppend'):
                menu.Append(submenu, label)

    def get_body(self, indent):
        """Returns the body of an inline method."""
        result = []
        while self.index < len(self.desc):
            line = self.desc[self.index]
            if (len(line) - len(line.lstrip())) <= indent:
                break
            result.append(line)
            self.index += 1
        result = "\n".join(result).rstrip()
        if result != "":
            return result
        return "  pass"

    def get_id(self, name):
        """Returns the ID associated with a specified name."""
        if isinstance(name, str):
            return self.names[name]
        return name

    def checked(self, name, check=None):
        """Checks (or unchecks) a menu item specified by name."""
        if check is None:
            return self.menu.IsChecked(self.get_id(name))
        self.menu.Check(self.get_id(name), check)

    def enabled(self, name, enable=None):
        """Enables (or disables) a menu item specified by name."""
        if enable is None:
            return self.menu.IsEnabled(self.get_id(name))
        self.menu.Enable(self.get_id(name), enable)

    def label(self, name, label=None):
        """Gets or sets the label for a menu item."""
        if label is None:
            return self.menu.GetLabel(self.get_id(name))
        self.menu.SetLabel(self.get_id(name), label)


class MakeMenuItem:
    """A menu item for a menu managed by MakeMenu."""

    def __init__(self, menu, id):
        self.menu = menu
        self.id = id

    def checked(self, check=None):
        return self.menu.checked(self.id, check)

    def toggle(self):
        checked = not self.checked()
        self.checked(checked)
        return checked

    def enabled(self, enable=None):
        return self.menu.enabled(self.id, enable)

    def label(self, label=None):
        return self.menu.label(self.id, label)


# -------------------------------------------------------------------------
#  Determine whether a string contains any specified option characters, and
#  remove them if it does:
# -------------------------------------------------------------------------


def option_check(test, string):
    """Determines whether a string contains any specified option characters,
    and removes them if it does.
    """
    result = []
    for char in test:
        col = string.find(char)
        result.append(col >= 0)
        if col >= 0:
            string = string[:col] + string[col + 1 :]
    return result + [string.strip()]


# -------------------------------------------------------------------------
#  Null menu option selection handler:
# -------------------------------------------------------------------------


def null_handler(event):
    print("null_handler invoked")
