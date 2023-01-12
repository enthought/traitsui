# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the various text editors for the wxPython user interface toolkit.
    The module is mainly a place-folder for TextEditor factories that have
    been augmented to also listen to changes in the items of the list object.

"""


from .text_editor import SimpleEditor as WXSimpleEditor
from .text_editor import CustomEditor as WXCustomEditor
from .text_editor import ReadonlyEditor as WXReadonlyEditor
from ..editors.csv_list_editor import _prepare_method, _dispose_method


class SimpleEditor(WXSimpleEditor):
    """Simple Editor style for CSVListEditor."""

    prepare = _prepare_method
    dispose = _dispose_method


class CustomEditor(WXCustomEditor):
    """Custom Editor style for CSVListEditor."""

    prepare = _prepare_method
    dispose = _dispose_method


class ReadonlyEditor(WXReadonlyEditor):
    """Readonly Editor style for CSVListEditor."""

    prepare = _prepare_method
    dispose = _dispose_method


TextEditor = SimpleEditor
