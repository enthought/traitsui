#------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#  
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#  
#  Author: Enthought, Inc.
#
#------------------------------------------------------------------------------

""" Enthought pyface package component
"""

# Standard library imports.
import os
import tempfile

# Major package imports.
import wx

# Enthought library imports.
from enthought.resource.api import ResourceFactory


class PyfaceResourceFactory(ResourceFactory):
    """ The implementation of a shared resource manager. """

    ###########################################################################
    # 'ResourceFactory' toolkit interface.
    ###########################################################################

    def image_from_file(self, filename):
        """ Creates an image from the data in the specified filename. """

        # N.B 'wx.BITMAP_TYPE_ANY' tells wxPython to attempt to autodetect the
        # --- image format.
        return wx.Image(filename, wx.BITMAP_TYPE_ANY)

    def image_from_data(self, data):
        """ Creates an image from the specified data. """

        # FIXME: There is currently no way in wx to create an image from data!
        # We have write it out to a temporary file and then read it back in!
        handle, filename = tempfile.mkstemp()

        # Write it out...
        tf = open(filename, 'wb')
        tf.write(data)
        tf.close()

        # ... and read it back in!  Lovely 8^()
        image = wx.Image(filename, wx.BITMAP_TYPE_ANY)

        # Remove the temporary file.
        os.close(handle)
        os.unlink(filename)
        
        return image

#### EOF ######################################################################
