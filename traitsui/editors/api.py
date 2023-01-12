# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" API for traitsui.editors subpackage.

Note that the following are also available from :mod:`traitsui.api`, which
is the preferred module for imports.

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

Tree Editor Actions / Traits
----------------------------
- :attr:`~.CopyAction`
- :attr:`~.CutAction`
- :attr:`~.DeleteAction`
- :attr:`~.IconSize`
- :attr:`~.NewAction`
- :attr:`~.PasteAction`
- :attr:`~.RenameAction`

"""

from ..toolkit import toolkit


try:
    from .array_editor import ArrayEditor
except ImportError:
    # check if failure is due to missing numpy, otherwise re-raise
    try:
        import numpy
    except ImportError:
        import warnings

        warnings.warn(
            "ArrayEditor is not available due to missing numpy", ImportWarning
        )
    else:
        del numpy
        raise

from .boolean_editor import BooleanEditor
from .button_editor import ButtonEditor
from .check_list_editor import CheckListEditor
from .code_editor import CodeEditor
from .color_editor import ColorEditor
from .compound_editor import CompoundEditor
from .csv_list_editor import CSVListEditor
from .custom_editor import CustomEditor
from .date_editor import DateEditor
from .datetime_editor import DatetimeEditor
from .date_range_editor import DateRangeEditor
from .styled_date_editor import StyledDateEditor
from .default_override import DefaultOverride
from .directory_editor import DirectoryEditor
from .dnd_editor import DNDEditor
from .drop_editor import DropEditor
from .enum_editor import EnumEditor
from .file_editor import FileEditor
from .font_editor import FontEditor
from .key_binding_editor import KeyBindingEditor
from .image_editor import ImageEditor
from .image_enum_editor import ImageEnumEditor
from .instance_editor import InstanceEditor
from .list_editor import ListEditor
from .list_str_editor import ListStrEditor
from .null_editor import NullEditor
from .range_editor import RangeEditor
from .rgb_color_editor import RGBColorEditor
from .set_editor import SetEditor
from .text_editor import TextEditor
from .table_editor import TableEditor
from .time_editor import TimeEditor
from .title_editor import TitleEditor
from .tree_editor import TreeEditor
from .tuple_editor import TupleEditor
from .history_editor import HistoryEditor
from .html_editor import HTMLEditor
from .popup_editor import PopupEditor
from .value_editor import ValueEditor
from .shell_editor import ShellEditor
from .scrubber_editor import ScrubberEditor
from .tabular_editor import TabularEditor
from .progress_editor import ProgressEditor
from .search_editor import SearchEditor

from traitsui.editors.tree_editor import (
    CopyAction,
    CutAction,
    DeleteAction,
    IconSize,
    NewAction,
    PasteAction,
    RenameAction,
)
