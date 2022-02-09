# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# tree_editor.py -- Example of a tree editor

from traits.api import HasTraits, Instance, List, Str, Regex
from traitsui.api import (
    Action,
    Group,
    Handler,
    HGroup,
    Item,
    Menu,
    Separator,
    TreeEditor,
    TreeNode,
    View,
    VSplit,
)
from traitsui.editors.tree_editor import (
    NewAction,
    CopyAction,
    CutAction,
    PasteAction,
    DeleteAction,
    RenameAction,
)


class Employee(HasTraits):
    name = Str('<unknown>')
    title = Str()
    phone = Regex(regex=r'\d\d\d-\d\d\d\d')

    def default_title(self):
        self.title = 'Senior Engineer'


class Department(HasTraits):
    name = Str('<unknown>')
    employees = List(Employee)


class Company(HasTraits):
    name = Str('<unknown>')
    departments = List(Department)
    employees = List(Employee)


class Owner(HasTraits):
    name = Str('<unknown>')
    company = Instance(Company)


jason = Employee(name='Jason', title='Engineer', phone='536-1057')
mike = Employee(name='Mike', title='Sr. Marketing Analyst', phone='536-1057')
dave = Employee(name='Dave', title='Sr. Engineer', phone='536-1057')
susan = Employee(name='Susan', title='Engineer', phone='536-1057')
betty = Employee(name='Betty', title='Marketing Analyst')

owner = Owner(
    name='wile',
    company=Company(
        name='Acme Labs, Inc.',
        departments=[
            Department(name='Marketing', employees=[mike, betty]),
            Department(name='Engineering', employees=[dave, susan, jason]),
        ],
        employees=[dave, susan, mike, betty, jason],
    ),
)

# View for objects that aren't edited
no_view = View()

# Actions used by tree editor context menu
def_title_action = Action(name='Default title', action='object.default')

dept_action = Action(
    name='Department',
    action='handler.employee_department(editor,object)',
)

# View used by tree editor
employee_view = View(
    VSplit(
        HGroup('3', 'name'),
        HGroup('9', 'title'),
        HGroup('phone'),
        id='vsplit',
    ),
    id='traits.doc.example.treeeditor',
    dock='vertical',
)


class TreeHandler(Handler):
    def employee_department(self, editor, object):
        dept = editor.get_parent(object)
        print(f'{object.name} works in the {dept.name} department.')


tree_editor = TreeEditor(
    nodes=[
        TreeNode(
            node_for=[Company],
            auto_open=True,
            children='',
            label='name',
            view=View(Group('name', orientation='vertical', show_left=True)),
        ),
        TreeNode(
            node_for=[Company],
            auto_open=True,
            children='departments',
            label='=Departments',
            view=no_view,
            add=[Department],
        ),
        TreeNode(
            node_for=[Company],
            auto_open=True,
            children='employees',
            label='=Employees',
            view=no_view,
            add=[Employee],
        ),
        TreeNode(
            node_for=[Department],
            auto_open=True,
            children='employees',
            label='name',
            menu=Menu(
                NewAction,
                Separator(),
                DeleteAction,
                Separator(),
                RenameAction,
                Separator(),
                CopyAction,
                CutAction,
                PasteAction,
            ),
            view=View(Group('name', orientation='vertical', show_left=True)),
            add=[Employee],
        ),
        TreeNode(
            node_for=[Employee],
            auto_open=True,
            label='name',
            menu=Menu(
                NewAction,
                Separator(),
                def_title_action,
                dept_action,
                Separator(),
                CopyAction,
                CutAction,
                PasteAction,
                Separator(),
                DeleteAction,
                Separator(),
                RenameAction,
            ),
            view=employee_view,
        ),
    ],
)

# The main view
view = View(
    Group(
        Item(name='company', id='company', editor=tree_editor, resizable=True),
        orientation='vertical',
        show_labels=True,
        show_left=True,
    ),
    title='Company Structure',
    id='traitsui.tests.tree_editor_test',
    dock='horizontal',
    drop_class=HasTraits,
    handler=TreeHandler(),
    buttons=['Undo', 'OK', 'Cancel'],
    resizable=True,
    width=0.3,
    height=0.3,
)

if __name__ == '__main__':
    owner.configure_traits(view=view)
