# Standard library imports.
import os

# Enthought library imports.
from traits.api import Any, HasTraits, List, Property, provides
from traits.api import Unicode

# Local imports.
from pyface.i_image_resource import IImageResource, MImageResource


@provides(IImageResource)
class ImageResource(MImageResource, HasTraits):
    """ The toolkit specific implementation of an ImageResource.  See the
    IImageResource interface for the API documentation.
    """

    # 'ImageResource' interface ----------------------------------------------

    #: The absolute path to the image resource.
    absolute_path = Property(Unicode)

    #: The name of the image resource for the resource manager.
    name = Unicode

    #: The search path to use when looking up the image.
    search_path = List

    # Private interface ------------------------------------------------------

    #: The resource manager reference for the image.
    _ref = Any

    # ------------------------------------------------------------------------
    # 'ImageResource' interface.
    # ------------------------------------------------------------------------

    def create_bitmap(self, size=None):
        return self.create_image(size)

    def create_icon(self, size=None):
        return self.create_image(size)

    def image_size(cls, image):
        """ Get the size of a toolkit image

        Parameters
        ----------
        image : toolkit image
            A toolkit image to compute the size of.

        Returns
        -------
        size : tuple
            The (width, height) tuple giving the size of the image.
        """
        # FIXME: can't do this without PIL or similar.
        return (0, 0)

    # ------------------------------------------------------------------------
    # Private interface.
    # ------------------------------------------------------------------------

    def _get_absolute_path(self):
        ref = self._get_ref()
        if ref is not None:
            absolute_path = os.path.abspath(self._ref.filename)

        else:
            absolute_path = self._get_image_not_found().absolute_path

        return absolute_path
