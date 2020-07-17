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
import os

import pkg_resources

from etsdemo.app import DemoPath, DemoVirtualDirectory


logger = logging.getLogger(__name__)

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

    e.g.:
    {
        "version": 1,
        "name": "Some Pretty Name",
        "root": "/path/to/folder",
    }

    """
    request = {}
    responses = []
    for entry_point in pkg_resources.iter_entry_points(ENTRY_POINT_GROUP):
        try:
            loader = entry_point.load()
        except ImportError:
            logger.exception("Failed to load entry point %r", entry_point)
            continue

        try:
            response = loader(request)
        except Exception:
            logger.exception("Failed to obtain data from %r", entry_point)
            continue
        responses.append(response)
    return responses


def response_to_node(response):
    """ Convert a response (dict) to an instance of DemoTreeNodeObject

    Parameters
    ----------
    response : dict
        Response obtained from an entry point.

    Returns
    -------
    node : DemoTreeNodeObject
    """
    root = response.get("root")
    if root is not None and not os.path.exists(root):
        return _get_placeholder_node(
            response,
            "Unable to load data: Path {!r} not found.".format(root)
        )

    try:
        return DemoPath(
            nice_name=response["name"],
            name=response["root"],
        )
    except KeyError:
        logger.exception("Failed to load response: %r", response)
        return _get_placeholder_node(
            response, "Unable to load data. See log for more info."
        )


def _get_placeholder_node(response, msg):
    """ Return a placeholder node if the response is malformed.

    Parameters
    ----------
    response : dict
        Response returned from a distribution's entry point.
    msg : str
        User-facing message to show.
    """
    return DemoVirtualDirectory(
        nice_name=response.get("name", "(Empty)"),
        resources=[],
        description=msg,
    )
