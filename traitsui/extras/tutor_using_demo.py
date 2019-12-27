#-------------------------------------------------------------------------
#
#  Copyright (c) 2020, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#-------------------------------------------------------------------------

""" A tutorial implemented using demo framework.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import, print_function

import sys

from pyface.image_resource import ImageResource
from traits.api import Bool, Button, Dict, HasTraits, Str
from traitsui.api import (
    CodeEditor, HGroup, HSplit, HTMLEditor, Item, ShellEditor, Tabbed,
    TitleEditor, ValueEditor, VGroup, View, VSplit
)
from traitsui.extras.demo import DemoFile
from traitsui.extras.tutor import LabHandler, NoDemo, StdOut


# The code for this class is copied from the old tutor.py code.
# xref #696
class TutorialFile(DemoFile):
    """ A demo file that also captures its output, exceptions.
    """
    #-- Trait Definitions-----------------------------------------------------

    auto_run = Bool(False)

    # User error message:
    message = Str

    # The output produced while the program is running:
    output = Str

    # The run Python code button:
    run = Button(image=ImageResource('run'), height_padding=1)

    # The dictionary containing the items from the Python code execution:
    values = Dict

    #-- Event Handlers -------------------------------------------------------

    def _run_changed(self):
        """ Runs the current set of snippet code.
        """
        self.run_code()

    #-- Public Methods -------------------------------------------------------

    def run_code(self):
        """ Runs all of the code snippets associated with the section.
        """
        # Reset any syntax error and message log values:
        self.message = self.output = ''

        # Redirect standard out and error to the message log:
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = StdOut(self)

        try:
            try:
                # Get the execution context dictionary:
                values = self.values

                # Clear out any special variables defined by the last run:
                for name in ('demo', 'popup'):
                    if isinstance(values.get(name), HasTraits):
                        del values[name]

                # Execute the current lab code:
                exec(self.source, values, values)

                # fixme: Hack trying to update the Traits UI view of the dict.
                self.values = {}
                self.values = values

                # Handle a 'demo' value being defined:
                demo = values.get('demo')
                if not isinstance(demo, HasTraits):
                    demo = NoDemo()
                self.demo = demo

                # Handle a 'popup' value being defined:
                popup = values.get('popup')
                if isinstance(popup, HasTraits):
                    popup.edit_traits(kind='livemodal')

            except SyntaxError as e:
                line = e.lineno
                if line is not None:
                    # Display the syntax error message:
                    self.message = '%s in column %s of line %s' % (
                                   e.msg.capitalize(), e.offset, line)
                else:
                    # Display the syntax error message without line # info:
                    self.message = e.msg.capitalize()
            except:
                import traceback
                traceback.print_exc()
        finally:
            # Restore standard out and error to their original values:
            sys.stdout, sys.stderr = stdout, stderr

    #-- Traits View Definitions ----------------------------------------------

    view = View(
        HSplit(
            Item(
                "description",
                label="Description",
                show_label=False,
                style="readonly",
                editor=HTMLEditor(format_text=True),
            ),
            VSplit(
                VGroup(
                    Item('source',
                         style='custom',
                         show_label=False,
                         ),
                    HGroup(
                        Item('run',
                             style='custom',
                             show_label=False,
                             tooltip='Run the Python code'
                             ),
                        '_',
                        Item('message',
                             springy=True,
                             show_label=False,
                             editor=TitleEditor()
                             ),
                        '_',
                        Item('visible',
                             label='View hidden sections'
                             )
                    ),
                    label='Lab',
                    dock='horizontal'
                ),
                Tabbed(
                    Item('values',
                         id='values_1',
                         label='Shell',
                         editor=ShellEditor(share=True),
                         dock='tab',
                         export='DockWindowShell'

                         ),
                    Item('values',
                         id='values_2',
                         editor=ValueEditor(),
                         dock='tab',
                         export='DockWindowShell'
                         ),
                    Item('output',
                         style='readonly',
                         editor=CodeEditor(show_line_numbers=False,
                                           selected_color=0xFFFFFF),
                         dock='tab',
                         export='DockWindowShell'
                         ),
                    Item('demo',
                         id='demo',
                         style='custom',
                         resizable=True,
                         dock='tab',
                         export='DockWindowShell'
                         ),
                    show_labels=False,
                ),
                label='Lab',
                dock='horizontal'
            ),
            id='splitter',
        ),
        id='enthought.tutor.tutor_file',
        handler=LabHandler
    )
