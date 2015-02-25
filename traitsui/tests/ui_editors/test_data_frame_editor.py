#  Copyright (c) 2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

import nose

from traits.api import HasTraits, Instance

from traitsui.item import Item
from traitsui.ui_editors.data_frame_editor import (
    DataFrameEditor, DataFrameAdapter)
from traitsui.view import View

from traitsui.tests._tools import *


class DataFrameViewer(HasTraits):

    data = Instance('pandas.core.frame.DataFrame')

    view = View(
        Item('data', editor=DataFrameEditor())
    )


def test_data_frame_editor():
    """ Basic smoke test for data frame editor """
    try:
        from pandas import DataFrame
    except ImportError as exc:
        print "Can't import Pandas: skipping"
        raise nose.SkipTest

    data = [[ 0,  1,  2],
            [ 3,  4,  5],
            [ 6,  7,  8],
            [ 9, 10, 11]]
    df = DataFrame(data, index=['one', 'two', 'three', 'four'],
                   columns=['X', 'Y', 'Z'])

    viewer = DataFrameViewer(data=df)

    with store_exceptions_on_all_threads():
        ui = viewer.edit_traits()
        ui.control.close()
