# (C) Copyright 2008-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# ------------------------------------------------------------------------------
# Copyright (c) 2007, Riverbank Computing Limited
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD license.
# However, when used with the GPL version of PyQt the additional terms described
# in the PyQt GPL exception also apply.
#
# Author: Riverbank Computing Limited
# ------------------------------------------------------------------------------

"""Creates a panel-based PyQt user interface for a specified UI object.
"""


from html import escape
import re

from pyface.qt import QtCore, QtGui

from traits.api import Any, HasPrivateTraits, Instance, Undefined
from traits.observation.api import match

from traitsui.api import Group

from traitsui.undo import UndoHistory

from traitsui.help_template import help_template

from traitsui.menu import UndoButton, RevertButton, HelpButton

from .helper import position_window

from .ui_base import BasePanel

from .editor import Editor


#: Characters that are considered punctuation symbols at the end of a label.
#: If a label ends with one of these charactes, we do not append a colon.
LABEL_PUNCTUATION_CHARS = "?=:;,.<>/\\\"'-+#|"

# Pattern of all digits
all_digits = re.compile(r"\d+")


# -------------------------------------------------------------------------
#  Create the different panel-based PyQt user interfaces.
# -------------------------------------------------------------------------


def ui_panel(ui, parent):
    """Creates a panel-based PyQt user interface for a specified UI object."""
    _ui_panel_for(ui, parent, False)


def ui_subpanel(ui, parent):
    """Creates a subpanel-based PyQt user interface for a specified UI object.
    A subpanel does not allow control buttons (other than those specified in
    the UI object) and does not show headers for view titles.
    """
    _ui_panel_for(ui, parent, True)


def _ui_panel_for(ui, parent, is_subpanel):
    """Creates a panel-based PyQt user interface for a specified UI object."""
    ui.control = control = _Panel(ui, parent, is_subpanel).control

    control._parent = parent
    control._object = ui.context.get("object")
    control._ui = ui

    try:
        ui.prepare_ui()
    except:
        control.setParent(None)
        del control
        ui.control = None
        ui.result = False
        raise

    ui.restore_prefs()
    ui.result = True


class _Panel(BasePanel):
    """PyQt user interface panel for Traits-based user interfaces."""

    def __init__(self, ui, parent, is_subpanel):
        """Initialise the object."""
        super().__init__(ui=ui)

        history = ui.history
        view = ui.view

        # Reset any existing history listeners.
        if history is not None:
            history.observe(
                self._on_undoable, "undoable", remove=True, dispatch="ui"
            )
            history.observe(
                self._on_redoable, "redoable", remove=True, dispatch="ui"
            )
            history.observe(
                self._on_revertable, "undoable", remove=True, dispatch="ui"
            )

        # Determine if we need any buttons or an 'undo' history.
        buttons = [self.coerce_button(button) for button in view.buttons]
        nr_buttons = len(buttons)
        has_buttons = not is_subpanel and (
            nr_buttons != 1 or not self.is_button(buttons[0], "")
        )

        if nr_buttons == 0:
            if view.undo:
                self.check_button(buttons, UndoButton)
            if view.revert:
                self.check_button(buttons, RevertButton)
            if view.help:
                self.check_button(buttons, HelpButton)

        if not is_subpanel and history is None:
            for button in buttons:
                if self.is_button(button, "Undo") or self.is_button(
                    button, "Revert"
                ):
                    history = ui.history = UndoHistory()
                    break

        # Create the panel.
        self.control = panel(ui)

        # Suppress the title if this is a subpanel or if we think it should be
        # superceded by the title of an "outer" widget (eg. a dock widget).
        title = view.title
        if (
            is_subpanel
            or (
                isinstance(parent, QtGui.QMainWindow)
                and not isinstance(parent.parent(), QtGui.QDialog)
            )
            or isinstance(parent, QtGui.QTabWidget)
        ):
            title = ""

        # Panels must be widgets as it is only the TraitsUI PyQt code that can
        # handle them being layouts as well.  Therefore create a widget if the
        # panel is not a widget or if we need a title or buttons.
        if (
            not isinstance(self.control, QtGui.QWidget)
            or title != ""
            or has_buttons
        ):
            w = QtGui.QWidget()
            layout = QtGui.QVBoxLayout(w)
            layout.setContentsMargins(0, 0, 0, 0)

            # Handle any view title.
            if title != "":
                layout.addWidget(heading_text(parent=w, text=view.title).control)

            if isinstance(self.control, QtGui.QWidget):
                layout.addWidget(self.control)
            elif isinstance(self.control, QtGui.QLayout):
                layout.addLayout(self.control)

            self.control = w

            # Add any buttons.
            if has_buttons:

                # Add the horizontal separator
                separator = QtGui.QFrame()
                separator.setFrameStyle(
                    QtGui.QFrame.Shadow.Sunken | QtGui.QFrame.Shape.HLine
                )
                separator.setFixedHeight(2)
                layout.addWidget(separator)

                # Add the special function buttons
                bbox = QtGui.QDialogButtonBox(QtCore.Qt.Orientation.Horizontal)
                for button in buttons:
                    role = QtGui.QDialogButtonBox.ButtonRole.ActionRole
                    if self.is_button(button, "Undo"):
                        self.undo = self.add_button(
                            button, bbox, role, self._on_undo, False, "Undo"
                        )
                        self.redo = self.add_button(
                            button, bbox, role, self._on_redo, False, "Redo"
                        )
                        history.observe(
                            self._on_undoable, "undoable", dispatch="ui"
                        )
                        history.observe(
                            self._on_redoable, "redoable", dispatch="ui"
                        )
                    elif self.is_button(button, "Revert"):
                        role = QtGui.QDialogButtonBox.ButtonRole.ResetRole
                        self.revert = self.add_button(
                            button, bbox, role, self._on_revert, False
                        )
                        history.observe(
                            self._on_revertable, "undoable", dispatch="ui"
                        )
                    elif self.is_button(button, "Help"):
                        role = QtGui.QDialogButtonBox.ButtonRole.HelpRole
                        self.add_button(button, bbox, role, self._on_help)
                    elif not self.is_button(button, ""):
                        self.add_button(button, bbox, role)
                layout.addWidget(bbox)

        # If the UI has a toolbar, should add it to the panel too
        self._add_toolbar(parent)

        # Ensure the control has a size hint reflecting the View specification.
        # Yes, this is a hack, but it's too late to repair this convoluted
        # control building process, so we do what we have to...
        self.control.sizeHint = _size_hint_wrapper(self.control.sizeHint, ui)

    def _add_toolbar(self, parent):
        """Adds a toolbar to the `parent` (QtWindow)"""
        if not isinstance(parent, QtGui.QMainWindow):
            # toolbar cannot be added to non-MainWindow widget
            return

        toolbar = self.ui.view.toolbar
        if toolbar is not None:
            self._last_group = self._last_parent = None
            qt_toolbar = toolbar.create_tool_bar(parent, self)
            qt_toolbar.setMovable(False)
            parent.addToolBar(qt_toolbar)
            self._last_group = self._last_parent = None

    def can_add_to_toolbar(self, action):
        """Returns whether the toolbar action should be defined in the user
        interface.
        """
        if action.defined_when == "":
            return True

        return self.ui.eval_when(action.defined_when)


def panel(ui):
    """Creates a panel-based PyQt user interface for a specified UI object.
    This function does not modify the UI object passed to it.  The object
    returned may be either a widget, a layout or None.
    """
    # Bind the context values to the 'info' object:
    ui.info.bind_context()

    # Get the content that will be displayed in the user interface:
    content = ui._groups
    nr_groups = len(content)

    if nr_groups == 0:
        panel = None
    if nr_groups == 1:
        panel = _GroupPanel(content[0], ui).control
    elif nr_groups > 1:
        panel = QtGui.QTabWidget()
        _fill_panel(panel, content, ui)
        panel.ui = ui

    # If the UI is scrollable then wrap the panel in a scroll area.
    if ui.scrollable and panel is not None:
        # Make sure the panel is a widget.
        if isinstance(panel, QtGui.QLayout):
            w = QtGui.QWidget()
            w.setLayout(panel)
            panel = w

        sa = QtGui.QScrollArea()
        sa.setWidget(panel)
        sa.setWidgetResizable(True)
        panel = sa

    return panel


def _fill_panel(panel, content, ui, item_handler=None):
    """Fill a page based container panel with content."""
    active = 0

    for index, item in enumerate(content):
        page_name = item.get_label(ui)
        if page_name == "":
            page_name = "Page %d" % index

        if isinstance(item, Group):
            if item.selected:
                active = index

            gp = _GroupPanel(item, ui, suppress_label=True)
            page = gp.control
            sub_page = gp.sub_control

            # If the result is the same type with only one page, collapse it
            # down into just the page.
            if isinstance(sub_page, type(panel)) and sub_page.count() == 1:
                new = sub_page.widget(0)
                if isinstance(panel, QtGui.QTabWidget):
                    sub_page.removeTab(0)
                else:
                    sub_page.removeItem(0)
            elif isinstance(page, QtGui.QWidget):
                new = page
            else:
                new = QtGui.QWidget()
                if page is not None:
                    new.setLayout(page)

            layout = new.layout()
            if layout is not None:
                layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)

        else:
            new = QtGui.QWidget()
            layout = QtGui.QVBoxLayout(new)
            layout.setContentsMargins(0, 0, 0, 0)
            item_handler(item, layout)

        # Add the content.
        if isinstance(panel, QtGui.QTabWidget):
            panel.addTab(new, page_name)
        else:
            panel.addItem(new, page_name)

    panel.setCurrentIndex(active)


def _size_hint_wrapper(f, ui):
    """Wrap an existing sizeHint method with sizes from a UI object."""

    def sizeHint():
        size = f()
        if ui.view is not None:
            if ui.view.width > 0:
                size.setWidth(int(ui.view.width))
            if ui.view.height > 0:
                size.setHeight(int(ui.view.height))
        return size

    return sizeHint


def show_help(ui, button):
    """Displays a help window for the specified UI's active Group."""
    group = ui._groups[ui._active_group]
    template = help_template()
    if group.help != "":
        header = template.group_help % escape(group.help)
    else:
        header = template.no_group_help
    fields = []
    for item in group.get_content(False):
        if not item.is_spacer():
            fields.append(
                template.item_help
                % (
                    escape(item.get_label(ui)),
                    escape(item.get_help(ui)),
                )
            )
    html_content = template.group_html % (header, "\n".join(fields))
    HTMLHelpWindow(button, html_content, 0.25, 0.33)


def show_help_popup(event):
    """Displays a pop-up help window for a single trait."""
    control = event.GetEventObject()
    template = help_template()

    # Note: The following check is necessary because under Linux, we get back
    # a control which does not have the 'help' trait defined (it is the parent
    # of the object with the 'help' trait):
    help = getattr(control, "help", None)
    if help is not None:
        html_content = template.item_html % (control.GetLabel(), help)
        HTMLHelpWindow(control, html_content, 0.25, 0.13)


class _GroupSplitter(QtGui.QSplitter):
    """A splitter for a Traits UI Group with layout='split'."""

    def __init__(self, group):
        """Store the group."""
        QtGui.QSplitter.__init__(self)
        self._group = group
        self._initialized = False

    def resizeEvent(self, event):
        """Overridden to position the splitter based on the Group when the
        application is initializing.

        Because the splitter layout algorithm requires that the available
        space be known, we have to wait until the UI that contains this
        splitter gives it its initial size.
        """
        QtGui.QSplitter.resizeEvent(self, event)

        parent = self.parent()
        if (
            not self._initialized
            and parent
            and (self.isVisible() or isinstance(parent, QtGui.QMainWindow))
        ):
            self._initialized = True
            self._resize_items()

    def showEvent(self, event):
        """Wait for the show event to resize items if necessary."""
        QtGui.QSplitter.showEvent(self, event)
        if not self._initialized:
            self._initialized = True
            self._resize_items()

    def _resize_items(self):
        """Size the splitter based on the 'width' or 'height' attributes
        of the Traits UI view elements.
        """
        use_widths = self.orientation() == QtCore.Qt.Orientation.Horizontal

        # Get the requested size for the items.
        sizes = []
        for item in self._group.content:
            if use_widths:
                sizes.append(item.width)
            else:
                sizes.append(item.height)

        # Find out how much space is available.
        if use_widths:
            total = self.width()
        else:
            total = self.height()

        # Allocate requested space.
        avail = total
        remain = 0
        for i, sz in enumerate(sizes):
            if avail <= 0:
                break

            if sz >= 0:
                if sz >= 1:
                    sz = min(sz, avail)
                else:
                    sz *= total

                sz = int(sz)
                sizes[i] = sz
                avail -= sz
            else:
                remain += 1

        # Allocate the remainder to those parts that didn't request a width.
        if remain > 0:
            remain = int(avail // remain)

            for i, sz in enumerate(sizes):
                if sz < 0:
                    sizes[i] = remain

        # If all requested a width, allocate the remainder to the last item.
        else:
            sizes[-1] += avail

        self.setSizes(sizes)


class _GroupPanel(object):
    """A sub-panel for a single group of items.  It may be either a layout or a
    widget.
    """

    def __init__(self, group, ui, suppress_label=False):
        """Initialise the object."""
        # Get the contents of the group:
        content = group.get_content()

        # Save these for other methods.
        self.group = group
        self.ui = ui

        if group.orientation == "horizontal":
            self.direction = QtGui.QBoxLayout.Direction.LeftToRight
        else:
            self.direction = QtGui.QBoxLayout.Direction.TopToBottom

        # outer is the top-level widget or layout that will eventually be
        # returned.  sub is the QTabWidget or QToolBox corresponding to any
        # 'tabbed' or 'fold' layout.  It is only used to collapse nested
        # widgets.  inner is the object (not necessarily a layout) that new
        # controls should be added to.
        outer = sub = inner = None

        # Get the group label.
        if suppress_label:
            label = ""
        else:
            label = group.label

        # Create a border if requested.
        if group.show_border:
            outer = QtGui.QGroupBox(label)
            inner = QtGui.QBoxLayout(self.direction, outer)

        elif label != "":
            outer = inner = QtGui.QBoxLayout(self.direction)
            inner.addWidget(heading_text(None, text=label).control)

        # Add the layout specific content.
        if len(content) == 0:
            pass

        elif group.layout == "flow":
            raise NotImplementedError("'the 'flow' layout isn't implemented")

        elif group.layout == "split":
            # Create the splitter.
            splitter = _GroupSplitter(group)
            splitter.setOpaqueResize(False)  # Mimic wx backend resize behavior
            if self.direction == QtGui.QBoxLayout.Direction.TopToBottom:
                splitter.setOrientation(QtCore.Qt.Orientation.Vertical)

            # Make sure the splitter will expand to fill available space
            policy = splitter.sizePolicy()
            policy.setHorizontalStretch(50)
            policy.setVerticalStretch(50)
            if group.orientation == "horizontal":
                policy.setVerticalPolicy(QtGui.QSizePolicy.Policy.Expanding)
            else:
                policy.setHorizontalPolicy(QtGui.QSizePolicy.Policy.Expanding)
            splitter.setSizePolicy(policy)

            if outer is None:
                outer = splitter
            else:
                inner.addWidget(splitter)

            # Create an editor.
            editor = SplitterGroupEditor(
                control=outer, splitter=splitter, ui=ui
            )
            self._setup_editor(group, editor)

            self._add_splitter_items(content, splitter)

        elif group.layout in ("tabbed", "fold"):
            # Create the TabWidget or ToolBox.
            if group.layout == "tabbed":
                sub = QtGui.QTabWidget()
            else:
                sub = QtGui.QToolBox()

            # Give tab/tool widget stretch factor equivalent to default stretch
            # factory for a resizeable item. See end of '_add_items'.
            policy = sub.sizePolicy()
            policy.setHorizontalStretch(50)
            policy.setVerticalStretch(50)
            sub.setSizePolicy(policy)

            _fill_panel(sub, content, self.ui, self._add_page_item)

            if outer is None:
                outer = sub
            else:
                inner.addWidget(sub)

            # Create an editor.
            editor = TabbedFoldGroupEditor(container=sub, control=outer, ui=ui)
            self._setup_editor(group, editor)

        else:
            if group.scrollable:
                # ensure a widget rather than a layout for the scroll area
                if outer is None:
                    outer = inner = QtGui.QBoxLayout(self.direction)
                if isinstance(outer, QtGui.QLayout):
                    widget = QtGui.QWidget()
                    widget.setLayout(outer)
                    outer = widget

                # now create a scroll area for the widget
                scroll_area = QtGui.QScrollArea()
                scroll_area.setWidget(outer)
                scroll_area.setWidgetResizable(True)
                outer = scroll_area

            # See if we need to control the visual appearance of the group.
            if group.visible_when != "" or group.enabled_when != "":
                # Make sure that outer is a widget and inner is a layout.
                # Hiding a layout is not properly supported by Qt (the
                # workaround in ``traitsui.qt.editor._visible_changed_helper``
                # often leaves undesirable blank space).
                if outer is None:
                    outer = inner = QtGui.QBoxLayout(self.direction)
                if isinstance(outer, QtGui.QLayout):
                    widget = QtGui.QWidget()
                    widget.setLayout(outer)
                    outer = widget

                # Create an editor.
                self._setup_editor(group, GroupEditor(control=outer))

            if isinstance(content[0], Group):
                layout = self._add_groups(content, inner)
            else:
                layout = self._add_items(content, inner)
            layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)

            if outer is None:
                outer = layout
            elif layout is not inner:
                inner.addLayout(layout)

        if group.style_sheet:
            if isinstance(outer, QtGui.QLayout):
                inner = outer
                outer = QtGui.QWidget()
                outer.setLayout(inner)

            # ensure this is not empty group
            if isinstance(outer, QtGui.QWidget):
                outer.setStyleSheet(group.style_sheet)

        # Publish the top-level widget, layout or None.
        self.control = outer

        # Publish the optional sub-control.
        self.sub_control = sub

    def _add_splitter_items(self, content, splitter):
        """Adds a set of groups or items separated by splitter bars."""
        for item in content:

            # Get a panel for the Item or Group.
            if isinstance(item, Group):
                panel = _GroupPanel(item, self.ui, suppress_label=True).control
            else:
                panel = self._add_items([item])

            # Add the panel to the splitter.
            if panel is not None:
                if isinstance(panel, QtGui.QLayout):
                    # A QSplitter needs a widget.
                    w = QtGui.QWidget()
                    panel.setContentsMargins(0, 0, 0, 0)
                    w.setLayout(panel)
                    panel = w

                layout = panel.layout()
                if layout is not None:
                    layout.setAlignment(
                        QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop
                    )

                splitter.addWidget(panel)

    def _setup_editor(self, group, editor):
        """Setup the editor for a group."""
        if group.id != "":
            self.ui.info.bind(group.id, editor)

        if group.visible_when != "":
            self.ui.add_visible(group.visible_when, editor)

        if group.enabled_when != "":
            self.ui.add_enabled(group.enabled_when, editor)

    def _add_page_item(self, item, layout):
        """Adds a single Item to a page based panel."""
        self._add_items([item], layout)

    def _add_groups(self, content, outer):
        """Adds a list of Group objects to the panel, creating a layout if
        needed.  Return the outermost layout.
        """
        # Use the existing layout if there is one.
        if outer is None:
            outer = QtGui.QBoxLayout(self.direction)

        # Process each group.
        for subgroup in content:
            panel = _GroupPanel(subgroup, self.ui).control

            if isinstance(panel, QtGui.QWidget):
                outer.addWidget(panel)
            elif isinstance(panel, QtGui.QLayout):
                outer.addLayout(panel)
            else:
                # The sub-group is empty which seems to be used as a way of
                # providing some whitespace.
                outer.addWidget(QtGui.QLabel(" "))

        return outer

    def _label_when(self):
        """Set the visible and enabled states of all labels as controlled by
        a 'visible_when' or 'enabled_when' expression.
        """
        self._evaluate_label_condition(self._label_enabled_whens, "enabled")
        self._evaluate_label_condition(self._label_visible_whens, "visible")

    def _evaluate_label_condition(self, conditions, kind):
        """Evaluates a list of (eval, widget) pairs and calls the appropriate
        method on the label widget to toggle whether it is visible/enabled
        as needed.
        """
        context = self.ui._get_context(self.ui.context)

        method_dict = {"visible": "setVisible", "enabled": "setEnabled"}

        for when, label in conditions:
            method_to_call = getattr(label, method_dict[kind])
            try:
                cond_value = eval(when, globals(), context)
                method_to_call(bool(cond_value))
            except Exception:
                # catch errors in the validate_when expression
                from traitsui.api import raise_to_debug

                raise_to_debug()

    def _add_items(self, content, outer=None):
        """Adds a list of Item objects, creating a layout if needed.  Return
        the outermost layout.
        """
        # Get local references to various objects we need:
        ui = self.ui
        info = ui.info
        handler = ui.handler

        group = self.group
        show_left = group.show_left
        columns = group.columns

        self._label_enabled_whens = []
        self._label_visible_whens = []

        # See if a label is needed.
        show_labels = False
        for item in content:
            show_labels |= item.show_label

        # See if a grid layout is needed.
        if show_labels or columns > 1:
            inner = QtGui.QGridLayout()

            if outer is None:
                outer = inner
            else:
                outer.addLayout(inner)

            row = 0
            if show_left:
                label_alignment = QtCore.Qt.AlignmentFlag.AlignRight
            else:
                label_alignment = QtCore.Qt.AlignmentFlag.AlignLeft

        else:
            # Use the existing layout if there is one.
            if outer is None:
                outer = QtGui.QBoxLayout(self.direction)

            inner = outer

            row = -1
            label_alignment = 0

        # Process each Item in the list:
        col = -1
        for item in content:

            # Keep a track of the current logical row and column unless the
            # layout is not a grid.
            col += 1
            if row >= 0 and col >= columns:
                col = 0
                row += 1

            # Get the name in order to determine its type:
            name = item.name

            # Convert a blank to a 5 pixel spacer:
            if name == " ":
                name = "5"

            # Check if is a label:
            if name == "":
                label = item.label
                if label != "":
                    self._add_label_item(item, inner, row, col, show_labels)

            # Check if it is a separator:
            elif name == "_":
                self._add_separator_item(
                    item, columns, inner, row, col, show_labels
                )

            # Check if it is a spacer:
            elif all_digits.match(name):
                self._add_spacer_item(item, name, inner, row, col, show_labels)

            else:
                # Otherwise, it must be a trait Item:
                object = eval(item.object_, globals(), ui.context)
                trait = object.base_trait(name)
                desc = trait.tooltip
                if desc is None:
                    desc = "Specifies " + trait.desc if trait.desc else ""

                # Get the editor factory associated with the Item:
                editor_factory = item.editor
                if editor_factory is None:
                    editor_factory = trait.get_editor().trait_set(
                        **item.editor_args
                    )

                    # If still no editor factory found, use a default text editor:
                    if editor_factory is None:
                        from .text_editor import ToolkitEditorFactory

                        editor_factory = ToolkitEditorFactory()

                    # If the item has formatting traits set them in the editor
                    # factory:
                    if item.format_func is not None:
                        editor_factory.format_func = item.format_func

                    if item.format_str != "":
                        editor_factory.format_str = item.format_str

                    # If the item has an invalid state extended trait name, set it
                    # in the editor factory:
                    if item.invalid != "":
                        editor_factory.invalid = item.invalid

                # Create the requested type of editor from the editor factory:
                factory_method = getattr(
                    editor_factory, item.style + "_editor"
                )
                editor = factory_method(
                    ui, object, name, item.tooltip, None
                ).trait_set(item=item, object_name=item.object)

                # Tell the editor to actually build the editing widget.  Note that
                # "inner" is a layout.  This shouldn't matter as individual editors
                # shouldn't be using it as a parent anyway.  The important thing is
                # that it is not None (otherwise the main TraitsUI code can change
                # the "kind" of the created UI object).
                editor.prepare(inner)
                control = editor.control

                if item.style_sheet:
                    control.setStyleSheet(item.style_sheet)

                # Set the initial 'enabled' state of the editor from the factory:
                editor.enabled = editor_factory.enabled

                # Handle any label.
                if item.show_label:
                    label = self._create_label(item, ui, desc)
                    self._add_widget(
                        inner, label, row, col, show_labels, label_alignment
                    )
                else:
                    label = None

                editor.label_control = label

                # Add emphasis to the editor control if requested:
                if item.emphasized:
                    self._add_emphasis(control)

                # If the item wants focus, remember the control so we can set focus
                # immediately before opening the UI.
                if item.has_focus:
                    self.ui._focus_control = control

                # Set the correct size on the control, as specified by the user:
                stretch = 0
                item_width = item.width
                item_height = item.height
                if (item_width != -1) or (item_height != -1):
                    is_horizontal = (
                        self.direction == QtGui.QBoxLayout.Direction.LeftToRight
                    )

                    min_size = control.minimumSizeHint()
                    width = min_size.width()
                    height = min_size.height()

                    force_width = False
                    force_height = False

                    if (0.0 < item_width <= 1.0) and is_horizontal:
                        stretch = int(100 * item_width)

                    item_width = int(item_width)
                    if item_width < -1:
                        item_width = -item_width
                        force_width = True
                    else:
                        item_width = max(item_width, width)

                    if (0.0 < item_height <= 1.0) and (not is_horizontal):
                        stretch = int(100 * item_height)

                    item_height = int(item_height)
                    if item_height < -1:
                        item_height = -item_height
                        force_height = True
                    else:
                        item_height = max(item_height, height)

                    control.setMinimumWidth(max(item_width, 0))
                    control.setMinimumHeight(max(item_height, 0))
                    if (stretch == 0 or not is_horizontal) and force_width:
                        control.setMaximumWidth(item_width)
                    if (stretch == 0 or is_horizontal) and force_height:
                        control.setMaximumHeight(item_height)

                # Set size and stretch policies
                self._set_item_size_policy(editor, item, label, stretch)

                # Add the created editor control to the layout
                # FIXME: Need to decide what to do about border_size and padding
                self._add_widget(inner, control, row, col, show_labels)

                # ---- Update the UI object

                # Bind the editor into the UIInfo object name space so it can be
                # referred to by a Handler while the user interface is active:
                id = item.id or name
                info.bind(id, editor, item.id)

                self.ui._scrollable |= editor.scrollable

                # Also, add the editors to the list of editors used to construct
                # the user interface:
                ui._editors.append(editor)

                # If the handler wants to be notified when the editor is created,
                # add it to the list of methods to be called when the UI is
                # complete:
                defined = getattr(handler, id + "_defined", None)
                if defined is not None:
                    ui.add_defined(defined)

                # If the editor is conditionally visible, add the visibility
                # 'expression' and the editor to the UI object's list of monitored
                # objects:
                if item.visible_when != "":
                    ui.add_visible(item.visible_when, editor)

                # If the editor is conditionally enabled, add the enabling
                # 'expression' and the editor to the UI object's list of monitored
                # objects:
                if item.enabled_when != "":
                    ui.add_enabled(item.enabled_when, editor)

        if (
            len(self._label_enabled_whens) + len(self._label_visible_whens)
        ) > 0:
            for object in self.ui.context.values():
                object.on_trait_change(
                    lambda: self._label_when(), dispatch="ui"
                )
            self._label_when()

        return outer

    def _add_label_item(self, item, inner, row, col, show_labels):
        label = item.label
        # Create the label widget.
        if item.style == "simple":
            label = QtGui.QLabel(label)
        else:
            label = heading_text(None, text=label).control

        self._add_widget(inner, label, row, col, show_labels)

        if item.emphasized:
            self._add_emphasis(label)

        if item.visible_when:
            self._label_visible_whens.append((item.visible_when, label))
        if item.enabled_when:
            self._label_enabled_whens.append((item.enabled_when, label))

    def _add_separator_item(self, item, columns, inner, row, col, show_labels):
        cols = columns

        # See if the layout is a grid.
        if row >= 0:
            # Move to the start of the row if necessary.
            if col > 0:
                col = 0

            # Allow for the columns.
            if show_labels:
                cols *= 2

        for i in range(cols):
            line = QtGui.QFrame()

            if self.direction == QtGui.QBoxLayout.Direction.LeftToRight:
                # Add a vertical separator:
                line.setFrameShape(QtGui.QFrame.Shape.VLine)
                if row < 0:
                    inner.addWidget(line)
                else:
                    inner.addWidget(line, i, row)
            else:
                # Add a horizontal separator:
                line.setFrameShape(QtGui.QFrame.Shape.HLine)
                if row < 0:
                    inner.addWidget(line)
                else:
                    inner.addWidget(line, row, i)

            line.setFrameShadow(QtGui.QFrame.Shadow.Sunken)

    def _add_spacer_item(self, item, name, inner, row, col, show_labels):

        # If so, add the appropriate amount of space to the layout:
        n = int(name)
        if self.direction == QtGui.QBoxLayout.Direction.LeftToRight:
            # Add a horizontal spacer:
            spacer = QtGui.QSpacerItem(n, 1)
        else:
            # Add a vertical spacer:
            spacer = QtGui.QSpacerItem(1, n)

        self._add_widget(inner, spacer, row, col, show_labels)

    def _set_item_size_policy(self, editor, item, label, stretch):
        """Set size policy of an item and its label (if any).

        How it is set:

        1) The general rule is that we obey the item.resizable and
           item.springy settings. An item is considered resizable also if
           resizable is Undefined but the item is scrollable

        2) However, if the labels are on the right, and the item is of a
           kind that cannot be stretched in horizontal (e.g. a checkbox),
           we make the label stretchable instead (to avoid big gaps
           between element and label)

        If the item is resizable, the _GroupPanel is set to be resizable.
        """

        is_label_left = self.group.show_left

        is_item_resizable = (item.resizable is True) or (
            (item.resizable is Undefined) and editor.scrollable
        )
        is_item_springy = item.springy

        # handle exceptional case 2)
        item_policy = editor.control.sizePolicy().horizontalPolicy()

        if (
            label is not None
            and not is_label_left
            and item_policy == QtGui.QSizePolicy.Policy.Minimum
        ):
            # this item cannot be stretched horizontally, and the label
            # exists and is on the right -> make label stretchable if necessary

            if (
                self.direction == QtGui.QBoxLayout.Direction.LeftToRight
                and is_item_springy
            ):
                is_item_springy = False
                self._make_label_h_stretchable(label, stretch or 50)

            elif (
                self.direction == QtGui.QBoxLayout.Direction.TopToBottom
                and is_item_resizable
            ):
                is_item_resizable = False
                self._make_label_h_stretchable(label, stretch or 50)

        if is_item_resizable:
            stretch = stretch or 50
            # FIXME: resizable is not defined as trait, were is it used?
            self.resizable = True
        elif is_item_springy:
            stretch = stretch or 50

        editor.set_size_policy(
            self.direction, is_item_resizable, is_item_springy, stretch
        )
        return stretch

    def _make_label_h_stretchable(self, label, stretch):
        """Set size policies of a QLabel to be stretchable horizontally.

        :attr:`stretch` is the stretch factor that Qt uses to distribute the
        total size to individual elements
        """
        label_policy = label.sizePolicy()
        label_policy.setHorizontalStretch(stretch)
        label_policy.setHorizontalPolicy(QtGui.QSizePolicy.Policy.Expanding)
        label.setSizePolicy(label_policy)

    def _add_widget(
        self,
        layout,
        w,
        row,
        column,
        show_labels,
        label_alignment=QtCore.Qt.AlignmentFlag(0),
    ):
        """Adds a widget to a layout taking into account the orientation and
        the position of any labels.
        """
        # If the widget really is a widget then remove any margin so that it
        # fills the cell.
        if isinstance(w, QtGui.QWidget):
            wl = w.layout()
            if wl is not None:
                wl.setContentsMargins(0, 0, 0, 0)

        # See if the layout is a grid.
        if row < 0:
            if isinstance(w, QtGui.QWidget):
                layout.addWidget(w)
            elif isinstance(w, QtGui.QLayout):
                layout.addLayout(w)
            else:
                layout.addItem(w)

        else:
            if self.direction == QtGui.QBoxLayout.Direction.LeftToRight:
                # Flip the row and column.
                row, column = column, row

            if show_labels:
                # Convert the "logical" column to a "physical" one.
                column *= 2

                # Determine whether to place widget on left or right of
                # "logical" column.
                if (label_alignment != 0 and not self.group.show_left) or (
                    label_alignment == 0 and self.group.show_left
                ):
                    column += 1

            if isinstance(w, QtGui.QWidget):
                layout.addWidget(w, row, column, label_alignment)
            elif isinstance(w, QtGui.QLayout):
                layout.addLayout(w, row, column, label_alignment)
            else:
                layout.addItem(w, row, column, 1, 1, label_alignment)

    def _create_label(self, item, ui, desc, suffix=":"):
        """Creates an item label.

        When the label is on the left of its component,
        it is not empty, and it does not end with a
        punctuation character (see :attr:`LABEL_PUNCTUATION_CHARS`),
        we append a suffix (by default a colon ':') at the end of the
        label text.

        We also set the help on the QLabel control (from item.help) and the
        tooltip (if the ``tooltip`` metadata on the edited trait exists, then
        it will be used as-is; otherwise, if the ``desc`` metadata exists, the
        string "Specifies " will be prepended to the start of ``desc``).

        Parameters
        ----------
        item : Item
            The item for which we want to create a label
        ui : UI
            Current ui object
        desc : string
            Description of the item, to create an appropriate tooltip
        suffix : string
            Characters to at the end of the label

        Returns
        -------
        label_control : QLabel
            The control for the label

        """

        label = item.get_label(ui)

        # append a suffix if the label is on the left and it does
        # not already end with a punctuation character
        if (
            label != ""
            and label[-1] not in LABEL_PUNCTUATION_CHARS
            and self.group.show_left
        ):
            label = label + suffix

        # create label controller
        label_control = QtGui.QLabel(label)

        if item.emphasized:
            self._add_emphasis(label_control)

        # FIXME: Decide what to do about the help.  (The non-standard wx way,
        # What's This style help, both?)
        # control.Bind(wx.EVT_LEFT_UP, show_help_popup)
        label_control.help = item.get_help(ui)

        if desc != "":
            label_control.setToolTip(desc)

        return label_control

    def _add_emphasis(self, control):
        """Adds emphasis to a specified control's font."""
        # Set the foreground colour.
        pal = QtGui.QPalette(control.palette())
        pal.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(0, 0, 127))
        control.setPalette(pal)

        # Set the font.
        font = QtGui.QFont(control.font())
        font.setBold(True)
        font.setPointSize(font.pointSize())
        control.setFont(font)


class GroupEditor(Editor):
    """A pseudo-editor that allows a group to be managed."""

    def __init__(self, **traits):
        """Initialise the object."""
        # We intentionally don't want to call Editor.__init__ here as
        # GroupEditor does its own thing. However, we still want Traits
        # machinery to be set up properly.
        HasPrivateTraits.__init__(self, **traits)
        self.trait_set(**traits)


class SplitterGroupEditor(GroupEditor):
    """A pseudo-editor that allows a group with a 'split' layout to be managed."""

    #: The QSplitter for the group
    splitter = Instance(_GroupSplitter)

    # -- UI preference save/restore interface ---------------------------------

    def restore_prefs(self, prefs):
        """Restores any saved user preference information associated with the
        editor.
        """
        if isinstance(prefs, dict):
            structure = prefs.get("structure")
        else:
            structure = prefs

        self.splitter._initialized = True
        self.splitter.restoreState(structure)

    def save_prefs(self):
        """Returns any user preference information associated with the editor."""
        return {"structure": self.splitter.saveState().data()}


class TabbedFoldGroupEditor(GroupEditor):
    """A pseudo-editor that allows a group with a 'tabbed' or 'fold' layout to
    be managed.
    """

    #: The QTabWidget or QToolBox for the group
    container = Any()

    # -- UI preference save/restore interface ---------------------------------

    def restore_prefs(self, prefs):
        """Restores any saved user preference information associated with the
        editor.
        """
        if isinstance(prefs, dict):
            current_index = prefs.get("current_index")
        else:
            current_index = prefs

        self.container.setCurrentIndex(int(current_index))

    def save_prefs(self):
        """Returns any user preference information associated with the editor."""
        return {"current_index": str(self.container.currentIndex())}


# -------------------------------------------------------------------------
#  'HTMLHelpWindow' class:
# -------------------------------------------------------------------------


class HTMLHelpWindow(QtGui.QDialog):
    """Window for displaying Traits-based help text with HTML formatting."""

    def __init__(self, parent, html_content, scale_dx, scale_dy):
        """Initializes the object."""
        # Local import to avoid a WebKit dependency when one isn't needed.
        from pyface.qt import QtWebKit

        QtGui.QDialog.__init__(self, parent)
        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create the html control
        html_control = QtWebKit.QWebView()
        html_control.setSizePolicy(
            QtGui.QSizePolicy.Policy.Expanding, QtGui.QSizePolicy.Policy.Expanding
        )
        html_control.setHtml(html_content)
        layout.addWidget(html_control)

        # Create the OK button
        bbox = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.StandardButton.Ok, QtCore.Qt.Orientation.Horizontal
        )
        bbox.accepted.connect(self.accept)
        layout.addWidget(bbox)

        # Position and show the dialog
        position_window(self, parent=parent)
        self.show()


# -------------------------------------------------------------------------
#  Creates a Pyface HeadingText control:
# -------------------------------------------------------------------------

HeadingText = None


def heading_text(*args, create=False, **kw):
    """Create a Pyface HeadingText control."""
    global HeadingText

    if HeadingText is None:
        from pyface.api import HeadingText

    widget = HeadingText(*args, create=create, **kw)
    widget.create()
    return widget
