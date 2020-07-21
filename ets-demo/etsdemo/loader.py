# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Module for loading example data files contributed by other distributions
via entry points.
"""

import logging

import pkg_resources

from traits.api import Directory, HasTraits, Range, Str, TraitError

from etsdemo.app import DemoPath, DemoVirtualDirectory


logger = logging.getLogger(__name__)

#: The entry point group name for other packages to contribute
#: data files.
ENTRY_POINT_GROUP = "etsdemo_data"


def get_responses():
    """ Load entry points and return the responses.

    Version 1 response should have the following format:
    {
        "version": 1,
        "name": <str>,
        "root": <str>,
    }

    Required keys:
    ``version``: int
        The version for the format of this response
    ``name``: str
        The main display name for the group of resources.
    ``root``: str
        The root directory where resource files are stored.

    Returns
    -------
    responses: list of dict
        Responses loaded from the entry points.
        Note that the content has not been sanitized nor validated.
    """
    request = {}
    responses = []
    for entry_point in pkg_resources.iter_entry_points(ENTRY_POINT_GROUP):
        try:
            loader = entry_point.load()
        except ImportError:
            logger.exception("Failed to load entry point %r", entry_point)
            continue

        # `request` is currently a placeholder for future extension of the API
        # without having to change the function signature.
        try:
            response = loader(request)
        except Exception:
            logger.exception("Failed to obtain data from %r", entry_point)
            continue
        responses.append(response)
    return responses


def response_to_node(response):
    """ Convert a response to an instance of DemoTreeNodeObject

    Parameters
    ----------
    response : any
        Response obtained from an entry point.
        It is expected to be a dict, but there is no guarantee so it can
        be anything.

    Returns
    -------
    node : DemoTreeNodeObject
    """

    # Still try to get the name if we can
    try:
        name = response["name"]
    except (TypeError, KeyError):
        name = "(Empty)"

    try:
        normalized = _Response(
            version=response["version"],
            name=response["name"],
            root=response["root"],
        )
    except (TypeError, KeyError, TraitError):
        logger.exception("Failed to load response: %r", response)
        return DemoVirtualDirectory(
            nice_name=str(name),
            resources=[],
            description="Unable to load data.",
        )

    return normalized.to_node()


class _Response(HasTraits):
    """ Object for normalizing the validating responses returned by entry
    points.
    """

    #: Version
    version = Range(low=0, high=1)

    #: Display name
    name = Str()

    #: Root directory for any nested data files.
    root = Directory(exists=True)

    def to_node(self):
        """ Return an instance of DemoTreeNodeObject from this response.
        """
        return DemoPath(
            nice_name=self.name,
            name=self.root,
        )
