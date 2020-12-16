# ------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/07/2004
#
# ------------------------------------------------------------------------------

""" API for the traitsui package.

Editor Factories
----------------
- :class:`~.BasicEditorFactory`
- :class:`~.EditorFactory`

Context Values
--------------

- :attr:`~.CV`
- :attr:`~.CVFloat`
- :attr:`~.CVInt`
- :attr:`~.CVStr`
- :func:`~.CVType`
- :class:`~.ContextValue`

Editors
-------
- :class:`~.Editor`
- :attr:`~.ArrayEditor`
- :attr:`~.BooleanEditor`
- :attr:`~.ButtonEditor`
- :attr:`~.CheckListEditor`
- :attr:`~.CodeEditor`
- :func:`~.ColorEditor`
- :attr:`~.CompoundEditor`
- :class:`~.CSVListEditor`
- :attr:`~.CustomEditor`
- :class:`~.DateEditor`
- :class:`~.DatetimeEditor`
- :attr:`~.DateRangeEditor`
- :class:`~.DefaultOverride`
- :attr:`~.DirectoryEditor`
- :attr:`~.DNDEditor`
- :attr:`~.DropEditor`
- :attr:`~.EnumEditor`
- :attr:`~.FileEditor`
- :func:`~.FontEditor`
- :attr:`~.HistoryEditor`
- :attr:`~.HTMLEditor`
- :attr:`~.KeyBindingEditor`
- :class:`~.ImageEditor`
- :attr:`~.ImageEnumEditor`
- :attr:`~.InstanceEditor`
- :attr:`~.ListEditor`
- :class:`~.ListStrEditor`
- :attr:`~.NullEditor`
- :class:`~.PopupEditor`
- :attr:`~.ProgressEditor`
- :attr:`~.RangeEditor`
- :func:`~.RGBColorEditor`
- :class:`~.ScrubberEditor`
- :class:`~.SearchEditor`
- :attr:`~.SetEditor`
- :attr:`~.ShellEditor`
- :attr:`~.StyledDateEditor`
- :attr:`~.TableEditor`
- :class:`~.TabularEditor`
- :attr:`~.TextEditor`
- :class:`~.TimeEditor`
- :attr:`~.TitleEditor`
- :attr:`~.TreeEditor`
- :attr:`~.TupleEditor`
- :attr:`~.ValueEditor`

Layout Support
--------------

- :class:`~.Group`
- :class:`~.HFlow`
- :class:`~.HGroup`
- :class:`~.HSplit`
- :class:`~.Tabbed`
- :class:`~.VFlow`
- :class:`~.VFold`
- :class:`~.VGrid`
- :class:`~.VGroup`
- :class:`~.VSplit`

Handlers
--------

- :class:`~.Controller`
- :class:`~.Handler`
- :class:`~.ModelView`
- :class:`~.ViewHandler`
- :func:`~.default_handler`

UI Items
--------

- :class:`~.Custom`
- :class:`~.Heading`
- :class:`~.Item`
- :class:`~.Label`
- :class:`~.Readonly`
- :class:`~.Spring`
- :class:`~.UCustom`
- :class:`~.UItem`
- :class:`~.UReadonly`
- :attr:`~.spring`

Menus and Actions
-----------------

- :class:`~.Action`
- :attr:`~.ActionGroup`
- :attr:`~.ApplyButton`
- :attr:`~.CancelButton`
- :attr:`~.CloseAction`
- :attr:`~.HelpAction`
- :attr:`~.HelpButton`
- :attr:`~.LiveButtons`
- :attr:`~.Menu`
- :attr:`~.MenuBar`
- :attr:`~.ModalButtons`
- :attr:`~.NoButton`
- :attr:`~.NoButtons`
- :attr:`~.OKButton`
- :attr:`~.OKCancelButtons`
- :attr:`~.PyFaceAction`
- :attr:`~.RedoAction`
- :attr:`~.RevertAction`
- :attr:`~.RevertButton`
- :attr:`~.Separator`
- :attr:`~.StandardMenuBar`
- :attr:`~.ToolBar`
- :attr:`~.UndoAction`
- :attr:`~.UndoButton`

Table UI
--------

- :class:`~.TabularAdapter`

Table column types:

- :class:`~.ExpressionColumn`
- :class:`~.ListColumn`
- :class:`~.NumericColumn`
- :class:`~.ObjectColumn`
- :class:`~.TableColumn`

Table filter types:

- :class:`~.EvalTableFilter`
- :class:`~.MenuTableFilter`
- :class:`~.RuleTableFilter`
- :class:`~.TableFilter`

Toolkit Object
--------------

- :func:`~.toolkit`

Custom Traits
-------------

- :attr:`~.Color`
- :func:`~.ColorTrait`
- :attr:`~.Font`
- :func:`~.FontTrait`
- :attr:`~.RGBColor`
- :func:`~.RGBColorTrait`

Custom UI Traits
----------------

- :attr:`~.Border`
- :attr:`~.HasBorder`
- :attr:`~.HasMargin`
- :attr:`~.Image`
- :attr:`~.Margin`
- :class:`~.StatusItem`

Tree UI
-------

- :class:`~.ITreeNode`
- :class:`~.ITreeNodeAdapter`
- :class:`~.MultiTreeNode`
- :class:`~.ObjectTreeNode`
- :class:`~.TreeNode`
- :class:`~.TreeNodeObject`

UI and UI Support
-----------------

- :class:`~.UI`
- :class:`~.UIInfo`

Undo Support
------------

- :class:`~.AbstractUndoItem`
- :class:`~.ListUndoItem`
- :class:`~.UndoHistory`
- :class:`~.UndoHistoryUndoItem`
- :class:`~.UndoItem`

View and View Elements
----------------------

- :class:`~.View`
- :class:`~.ViewElement`
- :class:`~.ViewSubElement`
- :mod:`~.view_elements`

Miscellaneous
-------------

- :func:`~.on_help_call`
- :func:`~.help_template`
- :class:`~.Include`
- :func:`~.auto_close_message`
- :func:`~.error`
- :func:`~.message`
- :attr:`~._constants`
- :attr:`~.WindowColor`
- :func:`~.raise_to_debug`

"""

from .basic_editor_factory import BasicEditorFactory

from .context_value import CV, CVFloat, CVInt, CVStr, CVType, ContextValue

from .editor import Editor

from .editor_factory import EditorFactory

try:
    from .editors.api import ArrayEditor
except ImportError:
    # ArrayEditor depends on numpy, so ignore if numpy is not present.
    pass

from .editors.api import (
    BooleanEditor,
    ButtonEditor,
    CheckListEditor,
    CodeEditor,
    ColorEditor,
    CompoundEditor,
    CustomEditor,
    CSVListEditor,
    DNDEditor,
    StyledDateEditor,
    DateEditor,
    DatetimeEditor,
    DateRangeEditor,
    DefaultOverride,
    DirectoryEditor,
    DropEditor,
    EnumEditor,
    FileEditor,
    FontEditor,
    HTMLEditor,
    HistoryEditor,
    ImageEditor,
    ImageEnumEditor,
    InstanceEditor,
    KeyBindingEditor,
    ListEditor,
    ListStrEditor,
    NullEditor,
    PopupEditor,
    ProgressEditor,
    RGBColorEditor,
    RangeEditor,
    ScrubberEditor,
    SearchEditor,
    SetEditor,
    ShellEditor,
    TableEditor,
    TabularEditor,
    TextEditor,
    TimeEditor,
    TitleEditor,
    TreeEditor,
    TupleEditor,
    ValueEditor,
)

from .group import (
    Group,
    HFlow,
    HGroup,
    HSplit,
    Tabbed,
    VFlow,
    VFold,
    VGrid,
    VGroup,
    VSplit,
)

from .handler import (
    Controller,
    Handler,
    ModelView,
    ViewHandler,
    default_handler,
)

from .help import on_help_call

from .help_template import help_template

from .include import Include

from .item import (
    Custom,
    Heading,
    Item,
    Label,
    Readonly,
    Spring,
    UCustom,
    UItem,
    UReadonly,
    spring,
)

from .menu import (
    Action,
    ActionGroup,
    ApplyButton,
    CancelButton,
    CloseAction,
    HelpAction,
    HelpButton,
    LiveButtons,
    Menu,
    MenuBar,
    ModalButtons,
    NoButton,
    NoButtons,
    OKButton,
    OKCancelButtons,
    PyFaceAction,
    RedoAction,
    RevertAction,
    RevertButton,
    Separator,
    StandardMenuBar,
    ToolBar,
    UndoAction,
    UndoButton,
)

from .message import auto_close_message, error, message

from .table_column import (
    ExpressionColumn,
    ListColumn,
    NumericColumn,
    ObjectColumn,
    TableColumn,
)

from .table_filter import (
    EvalTableFilter,
    MenuTableFilter,
    RuleTableFilter,
    TableFilter,
)

from .tabular_adapter import TabularAdapter

from .toolkit import toolkit

from .toolkit_traits import (
    Color,
    ColorTrait,
    Font,
    FontTrait,
    RGBColor,
    RGBColorTrait,
)

from .tree_node import (
    ITreeNode,
    ITreeNodeAdapter,
    MultiTreeNode,
    ObjectTreeNode,
    TreeNode,
    TreeNodeObject,
)

from .ui import UI

from .ui_info import UIInfo

from .ui_traits import Border, HasBorder, HasMargin, Image, Margin, StatusItem

from .undo import (
    AbstractUndoItem,
    ListUndoItem,
    UndoHistory,
    UndoHistoryUndoItem,
    UndoItem,
)

from .view import View

from .view_element import ViewElement, ViewSubElement

from . import view_elements

_constants = toolkit().constants()
WindowColor = _constants.get("WindowColor", 0xFFFFFF)


def raise_to_debug():
    """ When we would otherwise silently swallow an exception, call this instead
    to allow people to set the TRAITS_DEBUG environment variable and get the
    exception.
    """
    import os

    if os.getenv("TRAITS_DEBUG") is not None:
        raise
