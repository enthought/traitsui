from __future__ import absolute_import
import random

from pyface.api import GUI
from traits.api import Button, HasTraits, Instance, Int, List, Str
from traitsui.api import ObjectColumn, TableEditor, UItem, View
from traitsui.extras.progress_column import ProgressColumn


class Job(HasTraits):

    name = Str

    percent_complete = Int


class JobManager(HasTraits):

    jobs = List(Instance(Job))

    start = Button

    def populate(self):
        self.jobs = [
            Job(name='job %02d' % i, percent_complete=0)
            for i in range(1, 25)
        ]

    def process(self):
        for job in self.jobs:
            job.percent_complete = min(
                job.percent_complete + random.randint(0, 3), 100)

        if any(job.percent_complete < 100 for job in self.jobs):
            GUI.invoke_after(100, self.process)

    def _start_fired(self):
        self.populate()
        GUI.invoke_after(1000, self.process)

    view = View(
        UItem('jobs', editor=TableEditor(
            columns=[
                ObjectColumn(name='name'),
                ProgressColumn(name='percent_complete'),
            ]
        )),
        UItem('start'),
        resizable=True,
    )


demo = view = job_manager = JobManager()

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
