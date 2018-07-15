import re

from traitsui.base_panel import BasePanel
from traitsui.group import Group

import ipywidgets

# Pattern of all digits
all_digits = re.compile(r'\d+')


def ui_panel(ui, parent):
    _ui_panel_for(ui, parent, False)


def ui_subpanel(ui, parent):
    _ui_panel_for(ui, parent, True)


def _ui_panel_for(ui, parent, is_subpanel):
    ui.control = control = Panel(ui, parent, is_subpanel).control


class Panel(BasePanel):

    def __init__(self, ui, parent, is_subpanel):
        self.ui = ui
        history = ui.history
        view = ui.view

        # Reset any existing history listeners.
        if history is not None:
            history.on_trait_change(self._on_undoable, 'undoable', remove=True)
            history.on_trait_change(self._on_redoable, 'redoable', remove=True)
            history.on_trait_change(self._on_revertable, 'undoable',
                                    remove=True)

        # no buttons for now

        self.control = panel(ui)


def panel(ui):
    ui.info.bind_context()

    content = ui._groups
    n_groups = len(content)

    if n_groups == 0:
        panel = None
    elif n_groups == 1:
        panel = GroupPanel(content[0], ui).control
    elif n_groups > 1:
        panel = ipywidgets.Tab()
        _fill_panel(panel, content, ui)
        panel.ui = ui

    # not handling scrollable for now

    return panel


def _fill_panel(panel, content, ui, item_handler=None):
    """ Fill a page-based container panel with content. """

    active = 0

    for index, item in enumerate(content):
        page_name = item.get_label(ui)
        if page_name == "":
            page_name = "Page {}".format(index)

        if isinstance(item, Group):
            if item.selected:
                active = index

            gp = GroupPanel(item, ui, suppress_label=True)
            page = gp.control
            sub_page = gp.sub_control

            if isinstance(sub_page, type(panel)) and len(sub_page.children) == 1:
                new = sub_page.children[0]
            else:
                new = page

        else:
            new = item_handler(item)

        panel.children += (new,)
        panel.set_title(index, page_name)

    panel.selected_index = active


class GroupPanel(object):

    def __init__(self, group, ui, suppress_label=False):
        content = group.get_content()

        self.group = group
        self.ui = ui

        outer = sub = inner = None
        if group.label != "":
            if group.orientation == 'horizontal':
                outer = inner = ipywidgets.HBox()
            else:
                outer = inner = ipywidgets.VBox()
            inner.children += (ipywidgets.Label(value=group.label),)

        if len(content) == 0:
            pass
        elif group.layout == 'tabbed':
            sub = ipywidgets.Tab()
            _fill_panel(sub, content, self.ui, self._add_page_item)
            if outer is None:
                outer = sub
            else:
                inner.children += (sub,)
            editor = PagedGroupEditor(container=sub, control=sub, ui=ui)
            self._setup_editor(group, editor)
        elif group.layout == 'fold':
            sub = ipywidgets.Accordion()
            _fill_panel(sub, content, self.ui, self._add_page_item)
            if outer is None:
                outer = sub
            else:
                inner.children += (sub,)
            editor = PagedGroupEditor(container=sub, control=sub, ui=ui)
            self._setup_editor(group, editor)
        elif group.layout in {'split', 'flow'}:
            raise NotImplementedError("IPyWidgets backend does not have Split or Flow")
        else:
            if isinstance(content[0], Group):
                layout = self._add_groups(content, inner)
            else:
                layout = self._add_items(content, inner)

            if outer is None:
                outer = layout
            elif layout is not inner:
                inner.children += (layout,)

        self.control = outer
        self.sub_control = sub

    def _setup_editor(self, group, editor):
        if group.id != '':
            self.ui.info.bind(group.id, editor)
        if group.visible_when != '':
            self.ui.info.bind(group.visible_when, editor)
        if group.enabled_when != '':
            self.ui.info.bind(group.enabled_when, editor)

    def _add_page_item(self, item, layout):
        """Adds a single Item to a page based panel.
        """
        layout.children += (item,)

    def _add_groups(self, content, outer):
        if outer is None:
            if self.group.orientation == 'horizontal':
                outer = ipywidgets.HBox()
            else:
                outer = ipywidgets.VBox()

        for subgroup in content:
            panel = GroupPanel(subgroup, self.ui).control

            if panel is not None:
                outer.children += (panel,)
            else:
                # add some space
                outer.children += (ipywidgets.Label(value=' '),)

        return outer

    def _add_items(self, content, outer=None):
        ui = self.ui
        info = ui.info
        handler = ui.handler

        group = self.group
        show_left = group.show_left
        columns = group.columns

        show_labels = any(item.show_label for item in content)

        if show_labels or columns > 1:
            if self.group.orientation == 'horizontal':
                inner = ipywidgets.HBox()
            else:
                inner = ipywidgets.VBox()
            #inner = ipywidgets.GridBox()
            if outer is None:
                outer = inner
            else:
                outer.children += (inner,)

            row = 0

        else:
            if self.group.orientation == 'horizontal':
                outer = ipywidgets.HBox()
            else:
                outer = ipywidgets.VBox()
            inner = outer
            row = -1
            show_left = None

        col = -1
        for item in content:
            col += 1
            if row > 0 and col > columns:
                col = 0
                row += 1

            name = item.name
            if name == '':
                label = item.label
                if label != "":
                    label = ipywidgets.Label(value=label)
                    self._add_widget(inner, label, row, col, show_labels)
                continue

            if name == '_':
                # separator
                # XXX do nothing for now
                continue

            if name == ' ':
                name = '5'

            if all_digits.match(name):
                # spacer
                # XXX do nothing for now
                continue

            # XXX can we avoid evals for dots?
            print(item.object_, ui.context)
            obj = eval(item.object_, globals(), ui.context)
            print(obj)
            trait = obj.base_trait(name)
            desc = trait.desc if trait.desc is not None else ''

            editor_factory = item.editor
            if editor_factory is None:
                editor_factory = trait.get_editor().trait_set(
                    **item.editor_args)

                if editor_factory is None:
                    # FIXME grab from traitsui.editors instead
                    from .text_editor import ToolkitEditorFactory
                    editor_factory = ToolkitEditorFactory()

                if item.format_func is not None:
                    editor_factory.format_func = item.format_func

                if item.format_str != '':
                    editor_factory.format_str = item.format_str

                if item.invalid != '':
                    editor_factory.invalid = item.invalid

            factory_method = getattr(editor_factory, item.style + '_editor')
            editor = factory_method(
                ui, obj, name, item.tooltip, None
            ).trait_set(item=item, object_name=item.object)

            # Tell the editor to actually build the editing widget.  Note that
            # "inner" is a layout.  This shouldn't matter as individual editors
            # shouldn't be using it as a parent anyway.  The important thing is
            # that it is not None (otherwise the main TraitsUI code can change
            # the "kind" of the created UI object).
            editor.prepare(inner)
            control = editor.control

            editor.enabled = editor_factory.enabled
            if item.show_label:
                label = self._create_label(item, ui, desc)
                self._add_widget(inner, label, row, col, show_labels,
                                 show_left)
            else:
                label = None

            editor.label_control = label

            self._add_widget(inner, control, row, col, show_labels)

            # bind to the UIinfo
            id = item.id or name
            info.bind(id, editor, item.id)

            # add to the list of editors
            ui._editors.append(editor)

            # handler may want to know when the editor is defined
            defined = getattr(handler, id + '_defined', None)
            if defined is not None:
                ui.add_defined(defined)

            # add visible_when and enabled_when hooks
            if item.visible_when != '':
                ui.add_visible(item.visible_when, editor)
            if item.enabled_when != '':
                ui.add_enabled(item.enabled_when, editor)

        return outer

    def _add_widget(self, layout, w, row, column, show_labels,
                    label_alignment='left'):
        #print(layout)
        if row < 0:
            # we have an HBox or VBox
            layout.children += (w,)
        else:
            if self.group.orientation == 'vertical':
                row, column = column, row

            if show_labels:
                column *= 2

# if __name__ == '__main__':
#     from traitsui.api import VGroup, Item, View, UI, default_handler
#
#     test_view = View(
#         VGroup(
#             Item(name='', label='test'),
#             show_labels=False,
#         ),
#     )
#     ui = UI(view=test_view,
#         context={},
#         handler=default_handler(),
#         view_elements=None,
#         title=test_view.title,
#         id='',
#         scrollable=False)
#
#     #print(panel(ui))
