# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" This module contains functions used by toolkit specific implementation for
normalizing differences among toolkits (Qt and Wx).
"""


def check_key_compat(key):
    """Check if the given key is a unicode character within the range of
    values currently supported for emulating key sequences on both Qt and Wx
    textboxes.

    Parameters
    ----------
    key : str
        A unicode character

    Raises
    ------
    ValueError
        If the unicode character is not within the supported range of values.
    """
    # Support for more characters can be added when there are needs.
    if ord(key) < 32 or ord(key) >= 127:
        raise ValueError(
            f"Key {key!r} is currently not supported. "
            f"Supported characters between code point 32 - 126."
        )
