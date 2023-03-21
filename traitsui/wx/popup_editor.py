# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# FIXME: PopupEditor is a proxy class defined here just for backward
# compatibility. The class (which represents the editor factory) has been moved
# to the traitsui.editors.list_editor file.
from traitsui.editors.popup_editor import (
    _PopupEditor as BasePopupEditor,
    PopupEditor,
)

from .ui_editor import UIEditor

# -------------------------------------------------------------------------
#  '_PopupEditor' class:
# -------------------------------------------------------------------------


class _PopupEditor(BasePopupEditor, UIEditor):
    pass
