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
HTML editor

The HTML editor displays simple formatted HTML text in a Traits UI view.

If the text is held in an HTML trait, then the HTMLEditor is the default. If
the text is held in a Str trait, then you may specify the HTMLEditor explicitly
if you wish to display it as HTML.

The supported subset of HTML tags and features depends on the UI toolkit (WX or
QT). This editor does not support style sheets. It does not support WYSIWYG
editing of the text, though the unformatted text can be edited in a plain text
editor.

The HTML editor can optionally be configured to do simple formatting of lists
and paragraphs without HTML tags, by setting the editor's 'format_text'
parameter True.

Please refer to the `HTMLEditor API docs`_ for further information.

.. _HTMLEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.editors.html_editor.html#traitsui.editors.html_editor.HTMLEditor
"""

from traits.api import HasTraits, HTML
from traitsui.api import UItem, View, HTMLEditor

# Sample text to display as HTML: header, plus module docstring, plus
# some lists. The docstring and lists will be auto-formatted
# (format_text=True).
sample_text = (
    """
<html><body><h1>HTMLEditor example</h1>

"""
    + __doc__
    + """
<i>Here are some lists formatted in this way:</i>

Numbered list:
  * first
  * second
  * third

Bulleted list:
  - eat
  - drink
  - be merry
"""
)


class HTMLEditorDemo(HasTraits):
    """Defines the main HTMLEditor demo class."""

    # Define a HTML trait to view
    my_html_trait = HTML(sample_text)

    # Demo view
    traits_view = View(
        UItem(
            'my_html_trait',
            # we specify the editor explicitly in order to set format_text:
            editor=HTMLEditor(format_text=True),
        ),
        title='HTMLEditor',
        buttons=['OK'],
        width=800,
        height=600,
        resizable=True,
    )


# Create the demo:
demo = HTMLEditorDemo()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
