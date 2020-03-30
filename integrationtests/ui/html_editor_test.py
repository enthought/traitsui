#-------------------------------------------------------------------------
#
#  Test case for the HTMLEditor.
#
#  Written by: David C. Morrill
#
#  Date: 09/22/2005
#
#  (c) Copyright 2005 by Enthought, Inc.
#  License: BSD Style.
#
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from traits.api \
    import HasPrivateTraits, Code

from traitsui.api \
    import View, Group, Item, HTMLEditor

#-------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------

sample = """This is a code block:

    def foo ( bar ):
        print 'bar:', bar

This is an unordered list:
 - An
 - unordered
 - list

This is an ordered list:
 * One
 * Two
 * Three

Lists can be nested:
 * One
   * 1.1
   * 1.2
 * Two
   * 2.1
   * 2.2
"""

#-------------------------------------------------------------------------
#  'TestHTML' class:
#-------------------------------------------------------------------------


class TestHTML(HasPrivateTraits):

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Text string to display as HTML:
    html = Code(sample)

    #-------------------------------------------------------------------------
    #  Traits view definitions:
    #-------------------------------------------------------------------------

    view = View(Group(
        [Item('html#@', editor=HTMLEditor(format_text=True)), '|<>'],
        ['{Enter formatted text and/or HTML below:}@',
         'html#@', '|<>'],
        '|<>', layout='split'),
        title='HTML Editor Test',
        resizable=True,
        width=0.4,
        height=0.6)

#-------------------------------------------------------------------------
#  Run the test:
#-------------------------------------------------------------------------

if __name__ == '__main__':
    TestHTML().configure_traits()
