# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Creates a wizard-based wxPython user interface for a specified UI object.

    A wizard is a dialog box that displays a series of pages, which the user
    can navigate with forward and back buttons.
"""


import wx
import wx.adv as wz

from traits.api import Str, Union

from .constants import DefaultTitle
from .helper import restore_window, save_window, GroupEditor
from .ui_panel import fill_panel_for_group

# -------------------------------------------------------------------------
#  Trait definitions:
# -------------------------------------------------------------------------

# Trait that allows only None or a string value
none_str_trait = Union(None, Str, default_value="")


def ui_wizard(ui, parent):
    """Creates a wizard-based wxPython user interface for a specified UI
    object.
    """
    # Create the copy of the 'context' we will need while editing:
    ui._context = context = ui.context
    new_context = {
        name: None if value is None else value.clone_traits()
        for name, value in context.items()
    }
    ui.context = new_context

    # Now bind the context values to the 'info' object:
    ui.info.bind_context()

    # Create the wxPython wizard window:
    title = ui.view.title
    if title == "":
        title = DefaultTitle
    ui.control = wizard = wz.Wizard(parent, -1, title)

    # Create all of the wizard pages:
    pages = []
    editor_pages = []
    info = ui.info
    shadow_group = ui.view.content.get_shadow(ui)
    min_dx = min_dy = 0
    # Create a dictionary mapping each contained group in shadow_group to
    # its id and enabled_when fields.
    group_fields_mapping = {}
    for group in shadow_group.get_content():
        # FIXME: When the group's id or enabled_when or visible_when is
        # set, the "fill_panel_for_group" will create a new Panel to hold the
        # contents of the group (instead of adding them to the page itself).
        # This leads to an incorrect sizing of the panel(not sure why
        # actually): example would be 'test_ui2.py' in
        # Traits/integrationtests/ui. In addition,
        # it leads to incorrect bindings (of the id) on the UIInfo object:
        # the id is bound to the GroupEditor created in "fill_panel.."
        # instead of the PageGroupEditor created here.
        # A simple solution is to clear out these fields before calling
        # "fill_panel_for_group", and then reset these traits.
        group_fields_mapping[group] = (group.id, group.enabled_when)
        (group.id, group.enabled_when) = ("", "")
        page = UIWizardPage(wizard, editor_pages)
        pages.append(page)
        fill_panel_for_group(page, group, ui)

        # Size the page correctly, then calculate cumulative minimum size:
        sizer = page.GetSizer()
        sizer.Fit(page)
        size = sizer.CalcMin()
        min_dx = max(min_dx, size.GetWidth())
        min_dy = max(min_dy, size.GetHeight())

        # If necessary, create a PageGroupEditor and attach it to the right
        # places:
        (group.id, group.enabled_when) = group_fields_mapping[group]
        if group.id or group.enabled_when:
            page.editor = editor = PageGroupEditor(control=page)
            if group.id:
                page.id = group.id
                editor_pages.append(page)
                info.bind(page.id, editor)
            if group.enabled_when:
                ui.add_enabled(group.enabled_when, editor)

    # Size the wizard correctly:
    wizard.SetPageSize(wx.Size(min_dx, min_dy))

    # Set up the wizard 'page changing' event handler:
    wizard.Bind(wz.EVT_WIZARD_PAGE_CHANGING, page_changing)

    # Size the wizard and the individual pages appropriately:
    prev_page = pages[0]
    wizard.FitToPage(prev_page)

    # Link the pages together:
    for page in pages[1:]:
        page.SetPrev(prev_page)
        prev_page.SetNext(page)
        prev_page = page

    # Finalize the display of the wizard:
    try:
        ui.prepare_ui()
    except:
        ui.control.Destroy()
        ui.control.ui = None
        ui.control = None
        ui.result = False
        raise

    # Position the wizard on the display:
    ui.handler.position(ui.info)

    # Restore the user_preference items for the user interface:
    restore_window(ui)

    # Run the wizard:
    if wizard.RunWizard(pages[0]):
        # If successful, apply the modified context to the original context:
        original = ui._context
        for name, value in ui.context.items():
            if value is not None:
                original[name].copy_traits(value)
            else:
                original[name] = None
        ui.result = True
    else:
        ui.result = False

    # Clean up loose ends, like restoring the original context:
    wizard.Unbind(wz.EVT_WIZARD_PAGE_CHANGING, handler=page_changing)
    save_window(ui)
    ui.finish()
    ui.context = ui._context
    ui._context = {}


def page_changing(event):
    """Handles the user attempting to change the current wizard page."""
    # Get the page the user is trying to go to:
    page = event.GetPage()
    if event.GetDirection():
        new_page = page.GetNext()
    else:
        new_page = page.GetPrev()

    # If the page has a disabled PageGroupEditor object, veto the page change:
    if (
        (new_page is not None)
        and (new_page.editor is not None)
        and (not new_page.editor.enabled)
    ):
        event.Veto()

        # If their is a message associated with the editor, display it:
        msg = new_page.editor.msg
        if msg != "":
            wx.MessageBox(msg)


class UIWizardPage(wz.WizardPage):
    """A page within a wizard interface."""

    def __init__(self, wizard, pages):
        super().__init__(wizard)
        self.next = self.previous = self.editor = None
        self.pages = pages

    def SetNext(self, page):
        """Sets the next page after this one."""
        self.next = page

    def SetPrev(self, page):
        """Sets the previous page to this one."""
        self.previous = page

    def GetNext(self):
        """Returns the next page after this one."""
        editor = self.editor
        if (editor is not None) and (editor.next != ""):
            next_ = editor.next
            if next_ is None:
                return None
            for page in self.pages:
                if page.id == next_:
                    return page
        return self.next

    def GetPrev(self):
        """Returns the previous page to this one."""
        editor = self.editor
        if (editor is not None) and (editor.previous != ""):
            previous = editor.previous
            if previous is None:
                return None
            for page in self.pages:
                if page.id == previous:
                    return page
        return self.previous


class PageGroupEditor(GroupEditor):
    """Editor for a group, which displays a page."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: ID of next page to display
    next = none_str_trait
    #: ID of previous page to display
    previous = none_str_trait
    #: Message to display if user can't link to page
    msg = Str()
