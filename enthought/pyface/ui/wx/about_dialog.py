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
import sys

# Major package imports.
import wx
import wx.html
import wx.lib.wxpTag

# Enthought library imports.
from enthought.traits.api import implements, Instance, List, Unicode

# Local imports.
from enthought.pyface.i_about_dialog import IAboutDialog, MAboutDialog
from enthought.pyface.image_resource import ImageResource
from dialog import Dialog


_DIALOG_TEXT = '''
<html>
  <body>
    <center>
      <table width="100%%" cellspacing="4" cellpadding="0" border="0">
        <tr>
          <td align="center">
          <p>
            <img src="%s" alt="">
          </td>
        </tr>
      </table>

      <p>
      %s<br>
      <br>
      Python %s<br>
      wxPython %s<br>
      </p>
      <p>
      Copyright &copy; 2003-2010 Enthought, Inc.
      </p>

      <p>
        <wxp module="wx" class="Button">
          <param name="label" value="%s">
          <param name="id"    value="ID_OK">
        </wxp>
      </p>
  </center>
  </body>
</html>
'''


class AboutDialog(MAboutDialog, Dialog):
    """ The toolkit specific implementation of an AboutDialog.  See the
    IAboutDialog interface for the API documentation.
    """

    implements(IAboutDialog)

    #### 'IAboutDialog' interface #############################################

    additions = List(Unicode)

    image = Instance(ImageResource, ImageResource('about'))

    ###########################################################################
    # Protected 'IDialog' interface.
    ###########################################################################

    def _create_contents(self, parent):
        if parent.GetParent() is not None:
            title = parent.GetParent().GetTitle()

        else:
            title = ""

        # Set the title.
        self.title = "About %s" % title

        # Load the image to be displayed in the about box.
        image = self.image.create_image()
        path  = self.image.absolute_path

        # The additional strings.
        additions = '<br />'.join(self.additions)

        # The width of a wx HTML window is fixed (and  is given in the
        # constructor). We set it to the width of the image plus a fudge
        # factor! The height of the window depends on the content.
        width = image.GetWidth() + 80
        html = wx.html.HtmlWindow(parent, -1, size=(width, -1))

        # Get the version numbers.
        py_version = sys.version[0:sys.version.find("(")]
        wx_version = wx.VERSION_STRING

        # Get the text of the OK button.
        if self.ok_label is None:
            ok = "OK"
        else:
            ok = self.ok_label

        # Set the page contents.
        html.SetPage(
            _DIALOG_TEXT % (path, additions, py_version, wx_version, ok)
        )

        # Make the 'OK' button the default button.
        ok_button = html.FindWindowById(wx.ID_OK)
        ok_button.SetDefault()

        # Set the height of the HTML window to match the height of the content.
        internal = html.GetInternalRepresentation()
        html.SetSize((-1, internal.GetHeight()))

        # Make the dialog client area big enough to display the HTML window.
        # We add a fudge factor to the height here, although I'm not sure why
        # it should be necessary, the HTML window should report its required
        # size!?!
        width, height = html.GetSize()
        parent.SetClientSize((width, height + 10))

### EOF #######################################################################
