# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the file editor factory for all traits toolkit backends.
"""

from traits.api import Bool, File, Int, List, Str

from traitsui.editors.text_editor import TextEditor
from traitsui.group import Group
from traitsui.view import View

# -------------------------------------------------------------------------
#  Trait definitions:
# -------------------------------------------------------------------------

#: Wildcard filter:
filter_trait = List(Str)


class FileEditor(TextEditor):
    """Editor factory for file editors."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Wildcard filter to apply to the file dialog:
    filter = filter_trait

    #: Optional extended trait name of the trait containing the list of
    #: filters:
    filter_name = Str()

    #: Should file extension be truncated?
    truncate_ext = Bool(False)

    #: Can the user select directories as well as files?
    allow_dir = Bool(False)

    #: Is user input set on every keystroke? (Overrides the default) ('simple'
    #: style only):
    auto_set = False

    #: Is user input set when the Enter key is pressed? (Overrides the default)
    #: ('simple' style only):
    enter_set = True

    #: The number of history entries to maintain:
    #: FIXME: This is currently only supported on wx. Qt support needs to be
    #: added
    entries = Int(10)

    #: The root path of the file tree view ('custom' style only, not supported
    #: under wx). If not specified, the filesystem root is used.
    root_path = File()

    #: Optional extend trait name of the trait containing the root path.
    root_path_name = Str()

    #: Optional extended trait name used to notify the editor when the file
    #: system view should be reloaded ('custom' style only):
    reload_name = Str()

    #: Optional extended trait name used to notify when the user double-clicks
    #: an entry in the file tree view. The associated path is assigned it:
    dclick_name = Str()

    #: The style of file dialog to use when the 'Browse...' button is clicked
    #: Should be one of 'open' or 'save'
    dialog_style = Str("open")

    # -------------------------------------------------------------------------
    #  Traits view definition:
    # -------------------------------------------------------------------------

    traits_view = View(
        [
            [
                "<options>",
                "truncate_ext{Automatically truncate file extension?}",
                "|options:[Options]>",
            ],
            ["filter", "|[Wildcard filters]<>"],
        ]
    )

    extras = Group()


# This alias is deprecated and will be removed in TraitsUI 8.
ToolkitEditorFactory = FileEditor
