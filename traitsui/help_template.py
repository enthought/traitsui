# (C) Copyright 2004-2022 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" Defines the HTML help templates used for formatting Traits UI help pages.
"""

from traits.api import HasStrictTraits, Str


# Default HTML for a single Item's help window
ItemHTML = """
<HTML>
<BODY BGCOLOR="#E8E5D4">
<TABLE CELLPADDING="0">
  <TR>
    <TD BGCOLOR="#000000">
      <TABLE CELLSPACING = "1">
        <TR>
          <TD WIDTH="20%%" VALIGN="TOP" BGCOLOR="#9DB8F4"><B>%s</B></TD>
          <TD WIDTH="80%%" VALIGN="TOP" BGCOLOR="#C1D2F9">%s</TD>
        </TR>
      </TABLE>
    </TD>
  </TR>
</TABLE>
</BODY>
</HTML>"""

# Default HTML for a complete Group's help window
GroupHTML = """
<HTML>
<BODY BGCOLOR="#E8E5D4">%s
<TABLE CELLPADDING="0">
  <TR>
    <TD BGCOLOR="#000000">
      <TABLE CELLSPACING="1">%s</TABLE>
    </TD>
  </TR>
</TABLE>
</BODY>
</HTML>"""

# Default HTML for a single Item within a Group
ItemHelp = """
<TR>
  <TD WIDTH="20%%" VALIGN="TOP" BGCOLOR="#9DB8F4"><B>%s</B>:</TD>
  <TD WIDTH="80%%" VALIGN="TOP" BGCOLOR="#C1D2F9">%s</TD>
</TR>"""

# Default HTML for formatting a Group's 'help' trait
GroupHelp = """
<TABLE WIDTH="100%%" CELLPADDING="0">
  <TR>
    <TD BGCOLOR="#000000">
      <TABLE CELLSPACING="1">
        <TR>
          <TD BGCOLOR="#CDCDB6">%s</TD>
        </TR>
      </TABLE>
    </TD>
  </TR>
</TABLE>"""

# -------------------------------------------------------------------------
#  'HelpTemplate' class:
# -------------------------------------------------------------------------


class HelpTemplate(HasStrictTraits):
    """Contains HTML templates for displaying help."""

    item_html = Str(ItemHTML)  # Item popup help window HTML document
    group_html = Str(GroupHTML)  # Group help window HTML document
    item_help = Str(ItemHelp)  # Single group item HTML
    group_help = Str(GroupHelp)  # Group level help HTML
    no_group_help = Str("")  # Missing group level help HTML


# -------------------------------------------------------------------------
#  Gets/Sets the current HelpTemplate in use:
# -------------------------------------------------------------------------

_help_template = HelpTemplate()


def help_template(template=None):
    """Gets or sets the current HelpTemplate in use."""
    global _help_template

    if template is not None:
        _help_template = template
    return _help_template
