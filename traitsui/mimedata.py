# Import the toolkit specific version.
from __future__ import absolute_import
from traitsui.toolkit import toolkit_object

# WIP: Currently only supports qt4 backend. API might change without
# prior notification
PyMimeData = toolkit_object('clipboard:PyMimeData')
