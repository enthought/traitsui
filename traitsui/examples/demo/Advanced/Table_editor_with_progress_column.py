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
A demo to demonstrate the progress column in a TableEditor. The demo only works
with qt backend.
"""

import random

from pyface.api import GUI
from traits.api import Button, HasTraits, Instance, Int, List, observe, Str
from traitsui.api import ObjectColumn, TableEditor, UItem, View
from traitsui.extras.progress_column import ProgressColumn


class Job(HasTraits):

    name = Str()

    percent_complete = Int()


class JobManager(HasTraits):

    jobs = List(Instance(Job))

    start = Button()

    def populate(self):
        self.jobs = [
            Job(name='job %02d' % i, percent_complete=0) for i in range(1, 25)
        ]

    def process(self):
        for job in self.jobs:
            job.percent_complete = min(
                job.percent_complete + random.randint(0, 3), 100
            )

        if any(job.percent_complete < 100 for job in self.jobs):
            GUI.invoke_after(100, self.process)

    @observe('start')
    def _populate_and_process(self, event):
        self.populate()
        GUI.invoke_after(1000, self.process)

    traits_view = View(
        UItem(
            'jobs',
            editor=TableEditor(
                columns=[
                    ObjectColumn(name='name'),
                    ProgressColumn(name='percent_complete'),
                ]
            ),
        ),
        UItem('start'),
        resizable=True,
    )


demo = JobManager()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
