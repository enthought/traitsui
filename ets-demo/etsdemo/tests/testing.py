# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

import unittest
from unittest import mock

import pkg_resources


def require_gui(func):
    """ Decorator for tests that require a non-null GUI toolkit.
    """
    # Defer GUI import side-effect.
    # The toolkit is not resolved until we import pyface.api
    from pyface.api import GUI
    try:
        GUI()
    except NotImplementedError:
        return unittest.skip("No GUI available.")(func)
    return func


def create_iter_entry_points(fake_entry_points):
    """ Return a new callable that mocks the interface of
    pkg_resources.iter_entry_points with the given entry point data.

    Currently the behaviour of a given non-None value for ``name`` is not
    supported.

    Parameters
    ----------
    fake_entry_points : dict(str, dict)
        Mapping from distribution names to entry point definitions.
    """

    def iter_entry_points(group, name=None):

        if name is not None:
            # Mocking this logic is not currently needed.
            raise ValueError(
                "Currently the test code does not mock the behavior when name "
                "is not None."
            )

        for dist_name, group_to_entry_points in fake_entry_points.items():
            for entry_point_text in group_to_entry_points.get(group, []):
                entry_point = pkg_resources.EntryPoint.parse(
                    entry_point_text,
                    dist=pkg_resources.get_distribution(dist_name),
                )
                yield entry_point

    return iter_entry_points


def mock_iter_entry_points(fake_entry_points):
    """ Mock pkg_resources.iter_entry_points with the given entry point data.

    Currently the behaviour of a given non-None value for ``name`` is not
    supported.

    Parameters
    ----------
    fake_entry_points : dict(str, dict)
        Mapping from distribution names to entry point definitions.
    """
    return mock.patch.object(
        pkg_resources, "iter_entry_points",
        create_iter_entry_points(fake_entry_points)
    )
