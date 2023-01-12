# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# DataFrameEditor_demo.py -- Example of using dataframe editors

# Dataset from https://www.kaggle.com/mokosan/lord-of-the-rings-character-data
"""
**WARNING**

  This demo might not work as expected and some documented features might be
  missing.

-------------------------------------------------------------------------------

To run this demonstration successfully, you must have **pandas** installed.

Please refer to the `DataFrameEditor API docs`_ for further information.

.. _DataFrameEditor API docs: https://docs.enthought.com/traitsui/api/traitsui.ui_editors.data_frame_editor.html#traitsui.ui_editors.data_frame_editor.DataFrameEditor
"""
# Issue related to the demo warning: enthought/traitsui#944


import numpy as np
from pandas import DataFrame

from traits.api import HasTraits, Instance

from traitsui.api import View, Item
from traitsui.ui_editors.data_frame_editor import DataFrameEditor


class DataFrameEditorDemo(HasTraits):

    df = Instance(DataFrame)

    traits_view = View(
        Item(
            'df',
            show_label=False,
            editor=DataFrameEditor(
                formats={
                    'RuntimeInMinutes': '%.4d',
                    'BudgetInMillions': '%d',
                    'BoxOfficeRevenueInMillions': '%d',
                    'AcademyAwardNominations': '%d',
                    'AcademyAwardWins': '%d',
                    'RottenTomatoesScore': '%.2f',
                }
            ),
        ),
        title="DataFrameEditor",
        resizable=True,
        id='traitsui.demo.Applications.data_frame_editor_demo',
    )


# Sample Data
lotrMovieData = np.array(
    [
        [558, 281, 2917.0, 30, 17, 94.0],
        [178, 93, 871.5, 13, 4, 91.0],
        [179, 94, 926.0, 6, 2, 96.0],
        [201, 94, 1120, 11, 11, 95.0],
        [462.0, 675, 2932.0, 7, 1, 66.33333333],
        [169, 200, 1021.0, 3, 1, 64.0],
        [161, 217, 958.4, 3, 0, 75.0],
        [144, 250, 956.0, 1, 0, 60.0],
    ]
)

col_names = [
    'RuntimeInMinutes',
    'BudgetInMillions',
    'BoxOfficeRevenueInMillions',
    'AcademyAwardNominations',
    'AcademyAwardWins',
    'RottenTomatoesScore',
]

index_names = [
    'The Lord of the Rings Series',
    'The Fellowship of the Ring',
    'The Two Towers ',
    'The Return of the King',
    'The Hobbit Series',
    'The Unexpected Journey',
    'The Desolation of Smaug',
    'The Battle of the Five Armies',
]

# Create & run the demo
df = DataFrame(data=lotrMovieData, columns=col_names, index=index_names)

demo = DataFrameEditorDemo(df=df)

# Run the demo (if invoked from the command line):
if __name__ == '__main__':
    demo.configure_traits()
