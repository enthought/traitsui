import base64
import imghdr
import mimetypes
import os

# Enthought library imports.
from pyface.resource.api import ResourceFactory

mimetypes.init()


class PyfaceResourceFactory(ResourceFactory):
    """ The implementation of a shared resource manager. """

    # -------------------------------------------------------------------------
    # 'ResourceFactory' interface.
    # -------------------------------------------------------------------------

    def image_from_file(self, filename):
        """ Creates an image from the data in the specified filename. """

        path = os.path.relpath(filename)
        return path

    def image_from_data(self, data, filename=None):
        """ Creates an image from the specified data. """

        suffix = imghdr.what(filename, data)
        mimetype = mimetypes.suffix_map['.' + suffix]

        data_url = u"data:{};base64,{}".format(
            mimetype,
            base64.b64encode(data),
        )

        return data_url
