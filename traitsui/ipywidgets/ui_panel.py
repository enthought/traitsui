from traitsui.base_panel import BasePanel
from traitsui.group import Group

import ipywidgets


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

    content = ui._grousp
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

    for index, item in enumeratex(content):
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

        panel.children.append(new)
        panel.set_title(index, page_name)

    panel.selected_index = active


class GroupPanel(object):

    def __init__(self, group, ui, suppress_label=False):
        content = group.get_content()

        self.group = group
        self.ui = ui
