# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" The main function for launching the demo application.
"""
import argparse
import contextlib
import logging

from etsdemo.app import Demo, DemoVirtualDirectory
from etsdemo.loader import get_responses, response_to_node


#: Logging constants
_LOG_FORMAT = "%(asctime)s %(levelname)-8.8s [%(name)s:%(lineno)s] %(message)s"
logger = logging.getLogger(__name__)

#: Default application title
_TITLE = "Enthought Tool Suite"

_THIS_PACKAGE, _ = __name__.split(".", 1)


@contextlib.contextmanager
def _set_logger(logger, level):
    """ Context manager for setting logging.

    Parameters
    ----------
    logger : logging.Logger
        Logger to be configured.
    level : int
        Logging level to set.
    """
    formatter = logging.Formatter(_LOG_FORMAT)
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(formatter)

    original_level = logger.level
    logger.setLevel(level)
    logger.addHandler(handler)
    try:
        yield
    finally:
        logger.removeHandler(handler)
        logger.setLevel(original_level)


def _parse_command_line():
    """ Parse command line arguments for the main function.

    Returns
    -------
    namespace : argparse.Namespace
        Parsed command line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--debug',
        help="Log debugging information to console.",
        action="store_const",
        dest="log_level",
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument(
        '-v', '--verbose',
        help="Log information to console.",
        action="store_const",
        dest="log_level",
        const=logging.INFO,
    )
    return parser.parse_args()


def _create_demo(infos=None, title=_TITLE):
    """ Create the demo object with everything setup ready to be launched.

    Parameters
    ----------
    infos : list of dict, or None
        List of responses specifying the demo resources.
        Each response is a dictionary, in the format as specified by an
        entry point.
        If none, then responses are loaded from existing entry points installed
        in the Python environment.
    title : str, optional
        Default application title.

    Returns
    -------
    demo : Demo
    """
    if infos is None:
        infos = get_responses()

    resources = [
        response_to_node(response)
        for response in infos
    ]
    logger.info("Found %r resource(s).", len(resources))
    return Demo(
        title=title,
        model=DemoVirtualDirectory(resources=resources),
    )


def main(infos=None, title=_TITLE):
    """ Main function for launching the demo application.

    Parameters
    ----------
    infos : list of dict, or None
        List of responses specifying the demo resources.
        Each response is a dictionary, in the format as specified by an
        entry point. This allows packages to launch the demo application
        with their own set of data files without the entry points and without
        having to load files from other packages.
        If none, then responses are loaded from existing entry points installed
        in the Python environment.
    title : str, optional
        Default application title.
    """
    args = _parse_command_line()
    with _set_logger(logging.getLogger(_THIS_PACKAGE), level=args.log_level):
        demo = _create_demo(infos=infos, title=title)
        demo.configure_traits()
