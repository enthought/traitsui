# ------------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
#  All rights reserved.
#
#  This software is provided without warranty under the terms of the BSD
#  license included in LICENSE.txt and may be redistributed only
#  under the conditions described in the aforementioned license.  The license
#  is also available online at http://www.enthought.com/licenses/BSD.txt
#
#  Thanks for using Enthought open source!
#
#  Author: David C. Morrill
#  Date:   10/07/2004
#
# ------------------------------------------------------------------------------

""" Defines backward-compatible classes for older versions of Traits.
"""


try:
    from traits.api import PrefixList
except ImportError:
    def PrefixList(list_, default_value=None, **kwargs):
        from traits.api import Trait, TraitPrefixList
        if default_value is None:
            default_value = list_[0]
        return Trait(default_value, TraitPrefixList(list_), **kwargs)
