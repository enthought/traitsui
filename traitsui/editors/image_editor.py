#-------------------------------------------------------------------------------
#
#  Copyright (c) 2007, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   06/05/2007
#
#-------------------------------------------------------------------------------

""" Traits UI 'display only' image editor.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from __future__ import absolute_import

from traits.api import Bool, Property

from ..ui_traits import Image

from ..basic_editor_factory import BasicEditorFactory

from ..toolkit import toolkit_object

#-------------------------------------------------------------------------------
#  'ImageEditor' editor factory class:
#-------------------------------------------------------------------------------

class ImageEditor ( BasicEditorFactory ):

    # The editor class to be created:
    klass = Property

    # The optional image resource to be displayed by the editor (if not
    # specified, the editor's object value is used as the ImageResource to
    # display):
    image = Image

    # The following traits are currently supported on Qt only

    # Whether or not to scale the image to fit the available space
    scale = Bool
    
    # Whether or not to scale the image larger than the original when scaling
    allow_upscaling = Bool
    
    # Whether or not to preserve the aspect ratio when scaling
    preserve_aspect_ratio = Bool
    
    # Whether or not to allow the image to be clipped when not scaling
    allow_clipping = Bool


    def _get_klass(self):
        """ Returns the editor class to be instantiated.
        """
        return toolkit_object('image_editor:_ImageEditor')

#-- EOF -----------------------------------------------------------------------
