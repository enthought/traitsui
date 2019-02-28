#  Copyright (c) 2019, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in enthought/LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: Poruri Sai Rahul
#  Date:   Feb 2019

import six

if six.PY2:
    import string

    str_find = string.find
    str_rfind = string.rfind
else:
    str_find = str.find
    str_rfind = str.rfind
