#------------------------------------------------------------------------------
#
#  Copyright (c) 2005-19, Enthought, Inc.
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
#  Date:   10/25/2004
#
#------------------------------------------------------------------------------

""" Defines various helper functions that are useful for creating Traits-based
    user interfaces.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import

from operator import itemgetter

from traits.api import BaseTraitHandler, CTrait, Enum, TraitError

from .ui_traits import SequenceTypes
import six


#-------------------------------------------------------------------------
#  Trait definitions:
#-------------------------------------------------------------------------

# Layout orientation for a control and its associated editor
Orientation = Enum('horizontal', 'vertical')

# Docking drag bar style:
DockStyle = Enum('horizontal', 'vertical', 'tab', 'fixed')


def user_name_for(name):
    """ Returns a "user-friendly" name for a specified trait.
    """
    name = name.replace('_', ' ')
    name = name[:1].upper() + name[1:]
    result = ''
    last_lower = 0
    for c in name:
        if c.isupper() and last_lower:
            result += ' '
        last_lower = c.islower()
        result += c
    return result

#-------------------------------------------------------------------------
#  Format a number with embedded commas:
#-------------------------------------------------------------------------


def commatize(value):
    """ Formats a specified value as an integer string with embedded commas.
        For example: commatize( 12345 ) returns "12,345".
    """
    s = str(abs(value))
    s = s.rjust(((len(s) + 2) / 3) * 3)
    result = ','.join([s[i: i + 3] for i in range(0, len(s), 3)]).lstrip()
    if value >= 0:
        return result

    return '-' + result

#-------------------------------------------------------------------------
#  Recomputes the mappings for a new set of enumeration values:
#-------------------------------------------------------------------------


def enum_values_changed(values, strfunc=six.text_type):
    """ Recomputes the mappings for a new set of enumeration values.
    """

    if isinstance(values, dict):
        data = [(strfunc(v), n) for n, v in values.items()]
        if len(data) > 0:
            data.sort(key=itemgetter(0))
            col = data[0][0].find(':') + 1
            if col > 0:
                data = [(n[col:], v) for n, v in data]
    elif not isinstance(values, SequenceTypes):
        handler = values
        if isinstance(handler, CTrait):
            handler = handler.handler
        if not isinstance(handler, BaseTraitHandler):
            raise TraitError("Invalid value for 'values' specified")
        if handler.is_mapped:
            data = [(strfunc(n), n) for n in handler.map.keys()]
            data.sort(key=itemgetter(0))
        else:
            data = [(strfunc(v), v) for v in handler.values]
    else:
        data = [(strfunc(v), v) for v in values]

    names = [x[0] for x in data]
    mapping = {}
    inverse_mapping = {}
    for name, value in data:
        mapping[name] = value
        inverse_mapping[value] = name

    return (names, mapping, inverse_mapping)


def compute_column_widths(available_space, requested, min_widths, user_widths):
    """ Distribute column space amongst columns based on requested space.

    Widths requests can be specified as one of the following:

    - a value greater than 1.0 is treated as a fixed width with no flexibility
      (ie. a minimum width as specified and a weight of 0.0)

    - a value between 0.0 and 1.0 is treaded as a flexible width column with
      the specified width as a weight and a minimum width provided by the
      min_widths entry.

    - a value less than or equal to 0.0 is treated as a flexible width column
      with a weight of 0.1 and a minimum width provided by the min_widths
      parameter.

    If user widths are supplied then any non-None values override the
    requested widths, and are treated as having a flexibility of 0.

    Space is distributed by evaluating each column from smallest weight to
    largest and seeing if the weighted proportion of the remaining space is
    more than the minimum, and if so replacing the width with the weighted
    width.  The column is then removed from the available width and the
    total weight and the analysis continues.

    Parameters
    ----------
    available_space : int
        The available horizontal space.
    requested : list of numbers
        The requested width or weight for each column.
    min_widths : None or list of ints
        The minimum width for each flexible column
    user_widths : None or list of int or None
        Any widths specified by the user resizing the columns manually.

    Returns
    -------
    widths : list of ints
        The assigned width for each column
    """
    widths = []
    weights = []
    if min_widths is None:
        min_widths = [30] * len(requested)

    # determine flexibility and default width of each column
    for request, min_width in zip(requested, min_widths):
        if request >= 1.0:
            weights.append(0.0)
            widths.append(int(request))
        else:
            if request <= 0:
                weights.append(0.1)
            else:
                weights.append(request)
            widths.append(min_width)

    # if the user has changed the width of a column manually respect that
    if user_widths is not None:
        for i, user_width in enumerate(user_widths):
            if user_width is not None:
                widths[i] = user_width
                weights[i] = 0.0

    total_weight = sum(weights)
    if sum(widths) < available_space and total_weight > 0:
        # do inflexible first, then work up from smallest to largest
        for i, weight in sorted(enumerate(weights), key=itemgetter(1, 0)):
            total_weight = sum(weights)
            stretched = int(weight / total_weight * available_space)
            widths[i] = max(stretched, widths[i])

            # once we have dealt with a column, it no longer counts as flexible
            # and its space is no longer available
            weights[i] = 0.0
            available_space -= widths[i]

    return widths
