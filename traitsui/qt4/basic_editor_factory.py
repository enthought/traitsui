#------------------------------------------------------------------------------
#
#  Copyright (c) 2008, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#------------------------------------------------------------------------------

## Deprecated proxy for the BasicEditorFactory class declared in
# traitsui, declared here just for backward compatibility.

from __future__ import absolute_import
import warnings

from traitsui.basic_editor_factory \
    import BasicEditorFactory as AbstractBasicEditorFactory

#-------------------------------------------------------------------------
#  'BasicEditorFactory' class
#   Deprecated alias for traitsui.editor_factory.EditorFactory
#-------------------------------------------------------------------------


class BasicEditorFactory(AbstractBasicEditorFactory):
    """ Deprecated alias for
        traitsui.basic_editor_factory.BasicEditorFactory.
    """

    def __init__(self, *args, **kwds):
        super(BasicEditorFactory, self).__init__(*args, **kwds)
        warnings.warn("DEPRECATED: Use traitsui.basic_editor_factory"
                      ".BasicEditorFactory instead.", DeprecationWarning)

#---EOF-------------------------------------------------------------------
