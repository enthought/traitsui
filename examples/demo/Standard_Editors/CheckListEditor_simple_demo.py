"""
Checklist editor for a List of strings

The checklist editor provides a simple way for the user to select multiple items
from a list of known strings.

This example demonstrates the checklist editor's two most useful styles:

  * 'custom' displays all the strings in columns next to checkboxes.
  * 'readonly' displays only the selected strings, as a Python list of strings.

We do *not* demonstrate two styles which are not as useful for this editor:

  * 'text' is like 'readonly' except editable. It will accept a list of strings
    or numbers or even expressions. This is useful for quick, non-production
    data entry, but it ignores the editor's list of valid 'values'.
  * 'simple' (the default) only lets you select one item at a time, from a
    drop-down widget.
"""

from traits.api import HasTraits, List
from traitsui.api import UItem, Group, View, CheckListEditor, Label

class CheckListEditorDemo ( HasTraits ):
    """ Define the main CheckListEditor simple demo class. """

    # Specify the strings to be displayed in the checklist:
    checklist = List( editor = CheckListEditor(
                           values = [ 'one', 'two', 'three', 'four',
                                      'five', 'six'],
                           cols   = 2 ) )

    # CheckListEditor display with two columns:
    checklist_group = Group(
        '10', # insert vertical space
        Label('The custom style lets you select items from a checklist:'),
        UItem( 'checklist', style = 'custom'),
        '10','_','10',  # a horizontal line with 10 empty pixels above and below
        Label('The readonly style shows you which items are selected, '
              'as a Python list:'),
        UItem( 'checklist', style = 'readonly'),
    )

    traits_view = View(
        checklist_group,
        title     = 'CheckListEditor',
        buttons   = [ 'OK' ],
        resizable = True
    )

# Create the demo:
demo = CheckListEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

