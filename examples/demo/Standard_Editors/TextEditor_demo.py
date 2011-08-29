"""
Edit a string, password, or integer

The TextEditor displays a Str, Password, or Int trait for the user to edit.

When editing a Str, consider styles 'simple' (one-line), 'custom' (multi-line),
or read-only (multi-line).

When editing a Password, use style 'simple' (shows asterisks).

When editing an Int, consider styles 'simple' and 'readonly'.
"""
# FIXME:? as of 7/1/2011, Password style 'text' showed typed characters.
# It no longer does. Should it?

# Imports:
from traits.api import HasTraits, Str, Int, Password

from traitsui.api import Item, Group, View

# The main demo class:
class TextEditorDemo ( HasTraits ):
    """ Defines the TextEditor demo class.
    """

    # Define a trait for each of three TextEditor variants:
    string_trait = Str( "sample string" )
    int_trait    = Int( 1 )
    password     = Password

    # TextEditor display with multi-line capability (for a string):
    text_str_group = Group(
        Item( 'string_trait', style = 'simple',  label = 'Simple' ),
        Item( '_' ),
        Item( 'string_trait', style = 'custom',  label = 'Custom' ),
        Item( '_' ),
        # text style is the same as simple, not shown.
        Item( 'string_trait', style = 'readonly', label = 'ReadOnly' ),
        label = 'String'
    )

    # TextEditor display without multi-line capability (for an integer):
    text_int_group = Group(
        Item( 'int_trait', style = 'simple',   label = 'Simple' ),
        # custom and text styles are not useful for editing integers, not shown:
        Item( '_' ),
        Item( 'int_trait', style = 'readonly', label = 'ReadOnly' ),
        label = 'Integer'
    )

    # TextEditor display with secret typing capability (for Password traits):
    text_pass_group = Group(
        Item( 'password', style = 'simple',   label = 'Simple' ),
        # custom and text style are the same as simple, not shown.
        label = 'Password'
    )

    # The view includes one group per data type. These will be displayed
    # on separate tabbed panels:
    traits_view = View(
        text_str_group,
        text_pass_group,
        text_int_group,
        title   = 'TextEditor',
        buttons = [ 'OK' ]
    )

# Create the demo:
demo =  TextEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == "__main__":
    demo.configure_traits()
