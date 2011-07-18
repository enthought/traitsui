"""
Font editor

A Font editor in a Traits UI allows the user to select a font from the operating
system.

Typically, you then pass the Font trait to another UI editor, which uses it to
display text. You can also read the Font trait as a string, or access its
individual attributes (note that these attributes are specific to the UI toolkit
-- QT or WX.)

The default 'simple' Font editor style is usually the most useful and powerful
style - it pops up a font selection dialog which is specific to the OS and
toolkit.

This example also displays some other less common style choices.
"""

# Imports:
from traits.api import HasTraits, Font

from traitsui.api import Item, Group, View

class FontEditorDemo ( HasTraits ):
    """ Defines the main FontEditor demo class. """

    # Define a Font trait to view:
    my_font_trait = Font

    # Display specification (one Item per editor style):
    font_group = Group(
        Item( 'my_font_trait', style = 'simple',   label = 'Simple' ),
        Item( '_' ),
        Item( 'my_font_trait', style = 'custom',   label = 'Custom' ),
        Item( '_' ),
        Item( 'my_font_trait', style = 'text',     label = 'Text' ),
        Item( '_' ),
        Item( 'my_font_trait', style = 'readonly', label = 'ReadOnly' )
    )

    # Demo view:
    view = View(
        font_group,
        title     = 'FontEditor',
        buttons   = ['OK'],
        resizable = True
    )

# Create the demo:
demo = FontEditorDemo()


# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()

