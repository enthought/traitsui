#  Copyright (c) 2015, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt

from __future__ import absolute_import
from traitsui.ui_editors.data_frame_editor \
    import _DataFrameEditor as BaseDataFrameEditor

from .ui_editor import UIEditor


class _DataFrameEditor(BaseDataFrameEditor, UIEditor):
    """ Wx Toolkit implementation of the DataFrameEditor """
    pass
