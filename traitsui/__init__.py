#------------------------------------------------------------------------------
#
#  Copyright (c) 2005-2013, Enthought, Inc.
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
#  Date:   10/07/2004
#
#------------------------------------------------------------------------------

from __future__ import absolute_import

try:
    from traitsui._version import full_version as __version__
except ImportError:
    __version__ = 'not-built'

__requires__ = [
    'traits',
    'pyface>=6.0.0',
    'six',
]
__extras_require__ = {
    'wx': ['wxpython>=2.8.10', 'numpy'],
    'pyqt': ['pyqt>=4.10', 'pygments'],
    'pyqt5': ['pyqt>=5', 'pygments'],
    'pyside': ['pyside>=1.2', 'pygments'],
    'demo': ['configobj'],
}
