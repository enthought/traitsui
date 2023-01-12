# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""
Demonstrates an alternative method of defining a **TreeEditor** by creating
**ITreeNodeAdapter** subclasses.

To run this demonstration successfully, you must have **AppTools**
(``apptools``) installed.

Using **ITreeNodeAdapters** can be useful in cases where the kind of content
of the tree is not always known ahead of time. For example, you might be
creating a reusable tool or component which can display its data in a tree
view, but you do not know what kind of data it will be asked to display when
you write the code. Therefore, it may be impossible for you to specify a
**TreeEditor** with a correct set of **TreeNode** objects that will work
in all possible future cases.

Using **ITreeNodeAdapter** subclasses, you can allow the clients of your code
to solve this problem by providing one of more **ITreeNodeAdapters** that
can be used to provide the correct tree node information for each type of data
that will appear in the **TreeEditor** view.

In this demo, we define an **ITreeNodeAdapter** subclass that adapts the
*apptools.io.file.File* class to be displayed in a file explorer style
tree view.
"""

# -- Imports --------------------------------------------------------------

from os import getcwd

from traits.api import (
    HasTraits,
    Property,
    Directory,
    register_factory,
    cached_property
)

from traitsui.api import (
    View,
    VGroup,
    Item,
    TreeEditor,
    ITreeNode,
    ITreeNodeAdapter,
)

from apptools.io.api import File


# -- FileAdapter Class ----------------------------------------------------


class FileAdapter(ITreeNodeAdapter):

    # -- ITreeNodeAdapter Method Overrides ------------------------------------

    def allows_children(self):
        """Returns whether this object can have children."""
        return self.adaptee.is_folder

    def has_children(self):
        """Returns whether the object has children."""
        children = self.adaptee.children
        return (children is not None) and (len(children) > 0)

    def get_children(self):
        """Gets the object's children."""
        return self.adaptee.children

    def get_label(self):
        """Gets the label to display for a specified object."""
        return self.adaptee.name + self.adaptee.ext

    def get_tooltip(self):
        """Gets the tooltip to display for a specified object."""
        return self.adaptee.absolute_path

    def get_icon(self, is_expanded):
        """Returns the icon for a specified object."""
        if self.adaptee.is_file:
            return '<item>'

        if is_expanded:
            return '<open>'

        return '<open>'

    def can_auto_close(self):
        """Returns whether the object's children should be automatically
        closed.
        """
        return True


# -- FileTreeDemo Class ---------------------------------------------------


class FileTreeDemo(HasTraits):

    # The path to the file tree root:
    root_path = Directory(entries=10)

    # The root of the file tree:
    root = Property(observe='root_path')

    # The traits view to display:
    view = View(
        VGroup(
            Item('root_path'),
            Item('root', editor=TreeEditor(editable=False, auto_open=1)),
            show_labels=False,
        ),
        width=0.33,
        height=0.50,
        resizable=True,
    )

    # -- Traits Default Value Methods -----------------------------------------

    def _root_path_default(self):
        return getcwd()

    # -- Property Implementations ---------------------------------------------

    @cached_property
    def _get_root(self):
        return File(path=self.root_path)


# -- Create and run the demo ----------------------------------------------


register_factory(FileAdapter, File, ITreeNode)
demo = FileTreeDemo()

# Run the demo (if invoked form the command line):
if __name__ == '__main__':
    demo.configure_traits()
