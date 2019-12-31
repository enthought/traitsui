#-------------------------------------------------------------------------
#
#  Copyright (c) 2020, Enthought, Inc.
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
#  Date:   03/30/2007
#
#-------------------------------------------------------------------------

""" A tutorial implemented using demo framework.
"""

# The code in this module is copied from the old tutor.py code.
# xref #696


from __future__ import absolute_import, print_function

import operator
import os
import sys
import traceback

from pyface.image_resource import ImageResource
from traits.api import Bool, Button, Dict, HasTraits, Str
from traitsui.api import (
    CodeEditor, Handler, HGroup, HSplit, HTMLEditor, Item, ObjectTreeNode,
    ShellEditor, Tabbed, TextEditor, TitleEditor, TreeEditor, ValueEditor,
    VGroup, View, VSplit
)
from traitsui.extras.demo import (
    DemoFile, DemoPath, parse_source, path_view, publish_html_str
)


class _StdOut(object):
    """ Simulate stdout, but redirect the output to the 'output' string
        supplied by some 'owner' object.
    """

    def __init__(self, owner):
        self.owner = owner

    def flush(self):
        """ Flushes all current data to the output log.
        """
        pass

    def write(self, data):
        """ Adds the specified data to the output log.
        """
        self.owner.log += data


def _read_file(path, mode='rU', encoding='utf8'):
    """ Returns the contents of a specified text file (or None).

    """
    try:
        with open(path, mode, encoding=encoding) as fh:
            result = fh.read()
        return result
    except Exception:
        return None


# HTML template for displaying a .wmv/.avi movie file:
WMVMovieTemplate = """<html>
<head>
</head>
<body>
<p><object classid="clsid:22D6F312-B0F6-11D0-94AB-0080C74C7E95" codebase="http://activex.microsoft.com/activex/controls/mplayer/en/nsmp2inf.cab#Version=6,4,5,715">
<param name="FileName" value="%s">
<param name="AutoStart" value="true">
<param name="ShowTracker" value="true">
<param name="ShowControls" value="true">
<param name="ShowGotoBar" value="false">
<param name="ShowDisplay" value="false">
<param name="ShowStatusBar" value="false">
<param name="AutoSize" value="true">
<embed src="%s" AutoStart="true" ShowTracker="true" ShowControls="true" ShowGotoBar="false" ShowDisplay="false" ShowStatusBar="false" AutoSize="true" pluginspage="http://www.microsoft.com/windows/windowsmedia/download/"></object></p>
</body>
</html>
"""

# HTML template for displaying a QuickTime.mov movie file:
QTMovieTemplate = """<html>
<head>
</head>
<body>
<p><object classid="clsid:02BF25D5-8C17-4B23-BC80-D3488ABDDC6B" codebase="http://www.apple.com/qtactivex/qtplugin.cab" width="100%%" height="100%%">
<param name="src" value="file:///%s">
<param name="scale" value="aspect">
<param name="autoplay" value="true">
<param name="loop" value="false">
<param name="controller" value="true">
<embed src="file:///%s" width="100%%" height="100%%" scale="aspect" autoplay="true" loop="false" controller="true" pluginspage="http://www.apple.com/quicktime/download"></object></p>
</body>
</html>
"""

# HTML template for displaying an image file:
ImageTemplate = """<html>
<head>
</head>
<body>
<img src="%s">
</body>
</html>
"""

# HTML template for playing an MP3 audio file:
MP3Template = """<html>
<head>
<bgsound src="%s">
</head>
<body>
<p>&nbsp;</p>
</body>
</html>
"""


class TutorialHTMLFile(DemoFile):
    pass


tutorial_html_view = View(
    Item(
        "description",
        label="Description",
        show_label=False,
        style="readonly",
        editor=HTMLEditor(format_text=True),
    )
)


class TutorialFile(DemoFile):
    """ A demo file that also captures its output, exceptions.
    """
    #-- Trait Definitions-----------------------------------------------------

    #: Run code on gui initialization.
    auto_run = Bool(False)

    #: User error message
    message = Str

    #: The run Python code button
    run = Button(image=ImageResource('run'), height_padding=1)

    #: The dictionary containing the items from the Python code execution
    values = Dict

    #-- Event Handlers -------------------------------------------------------

    def _run_changed(self):
        """ Listener for run button.
        """
        self.run_code()

    #-- Public Methods -------------------------------------------------------

    def run_code(self):
        """ Runs the code.
        """
        # Reset any syntax error and message log values:
        self.message = self.log = ''

        # Redirect standard out and error to the message log:
        stdout, stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = _StdOut(self)

        try:
            try:
                # Get the execution context dictionary:
                values = self.values

                # Clear out any special variables defined by the last run:
                for name in ('demo', 'popup'):
                    if isinstance(values.get(name), HasTraits):
                        del values[name]

                # Execute the current lab code:
                exec(self.source, values, values)

                # fixme: Hack trying to update the Traits UI view of the dict.
                self.values = {}
                self.values = values

                # Handle a 'demo' value being defined:
                demo = values.get('demo')
                if isinstance(demo, HasTraits):
                    self.demo = demo
                else:
                    self.message = "No demo defined for this class."

                # Handle a 'popup' value being defined:
                popup = values.get('popup')
                if isinstance(popup, HasTraits):
                    popup.edit_traits(kind='livemodal')
            except SyntaxError as e:
                line = e.lineno
                if line is not None:
                    # Display the syntax error message:
                    self.message = '%s in column %s of line %s' % (
                        e.msg.capitalize(), e.offset, line)
                else:
                    # Display the syntax error message without line # info:
                    self.message = e.msg.capitalize()
            except Exception:
                traceback.print_exc()
        finally:
            # Restore standard out and error to their original values:
            sys.stdout, sys.stderr = stdout, stderr


class TutorialFileHandler(Handler):
    """ Controller for TutorialFile
    """

    def init(self, info):
        """ Handles initialization of the view.
        """
        # Run the code if the 'auto-run' feature is enabled:
        if info.object.auto_run:
            info.object.run_code()


tutor_file_view = View(
    HSplit(
        Item(
            "description",
            label="Description",
            show_label=False,
            style="readonly",
            editor=HTMLEditor(format_text=True),
        ),
        VSplit(
            VGroup(
                Item(
                    'source',
                    style='custom',
                    show_label=False,
                ),
                HGroup(
                    Item(
                        'run',
                        style='custom',
                        show_label=False,
                        tooltip='Run the Python code'
                    ),
                    '_',
                    Item(
                        'message',
                        springy=True,
                        show_label=False,
                        editor=TitleEditor()
                    )
                ),
                label='Lab',
                dock='horizontal'
            ),
            Tabbed(
                Item(
                    'values',
                    label='Shell',
                    editor=ShellEditor(share=True),
                    dock='tab',
                    export='DockWindowShell'
                ),
                Item(
                    'values',
                    editor=ValueEditor(),
                    dock='tab',
                    export='DockWindowShell'
                ),
                Item(
                    'log',
                    style='readonly',
                    label='Output',
                    editor=CodeEditor(
                        show_line_numbers=False,
                        selected_color=0xFFFFFF
                    ),
                    dock='tab',
                    export='DockWindowShell'
                ),
                Item(
                    'demo',
                    style='custom',
                    resizable=True,
                    dock='tab',
                    export='DockWindowShell'
                ),
                show_labels=False,
            ),
            label='Lab',
            dock='horizontal'
        ),
    ),
    handler=TutorialFileHandler
)


class TutorialTxtFile(DemoFile):
    description = Str


tutorial_text_view = View(
    Item(
        "description",
        label="Description",
        show_label=False,
        style="readonly",
        editor=TextEditor()
    )
)


class TutorialPath(DemoPath):
    """ A tutorial path also parses file extensions other than py.
    """

    def get_children_from_datastructure(self):
        dirs = []
        files = []
        path = self.path
        for name in os.listdir(path):
            cur_path = os.path.join(path, name)
            if os.path.isdir(cur_path):
                dirs.append(TutorialPath(name=name, parent=self))
            elif self.use_files:
                name, ext = os.path.splitext(name)

                # If we have a handler for the file type, invoke it:
                method = getattr(
                    self,
                    '_parse_%s_file' % ext[1:].lower(),
                    None
                )
                if method is not None:
                    files.append(method(cur_path, name))

        sort_key = operator.attrgetter("name")
        dirs.sort(key=sort_key)
        files.sort(key=sort_key)

        return dirs + files

    #-- Factory Methods for Creating Tutorial Files Based on File Type --------

    def _parse_avi_file(self, path, name):
        """ Parse a avi file
        """
        return self._parse_wmv_file(path, name)

    def _parse_htm_file(self, path, name):
        """ Parse a htm file
        """
        html = _read_file(path)
        return TutorialHTMLFile(description=html, name=name, parent=self)

    def _parse_html_file(self, path, name):
        """ Parse a html file
        """
        return self._parse_htm_file(path, name)

    def _parse_jpg_file(self, path, name):
        """ Parse a jpg file
        """
        html = ImageTemplate % path
        return TutorialHTMLFile(description=html, name=name, parent=self)

    def _parse_jpeg_file(self, path, name):
        """ Parse a jpeg file
        """
        return self._parse_jpg_file(path, name)

    def _parse_mov_file(self, path, name):
        """ Parse a mov file
        """
        path2 = path.replace(':', '|')
        html = QTMovieTemplate % (path2, path2)
        return TutorialHTMLFile(description=html, name=name, parent=self)

    def _parse_mp3_file(self, path, name):
        """ Parse a mp3 file
        """
        html = MP3Template % path
        return TutorialHTMLFile(description=html, name=name, parent=self)

    def _parse_png_file(self, path, name):
        """ Parse a png file
        """
        return self._parse_jpg_file(path, name)

    def _parse_py_file(self, path, name):
        """  Parse a py file
        """
        description, source = parse_source(path)
        description = publish_html_str(description)
        return TutorialFile(
            description=description,
            name=name,
            parent=self,
            source=source
        )

    def _parse_rst_file(self, path, name):
        """ Parse a rst file
        """
        rst_str = _read_file(path)
        html_str = publish_html_str(rst_str)
        return TutorialHTMLFile(description=html_str, name=name, parent=self)

    def _parse_txt_file(self, path, name):
        """ Parse a txt file
        """
        text = _read_file(path)
        return TutorialTxtFile(description=text, name=name, parent=self)

    def _parse_wmv_file(self, path, name):
        """ Parse a wmv file
        """
        html = WMVMovieTemplate % (path, path)
        return TutorialHTMLFile(description=html, name=name, parent=self)


tutor_tree_editor = TreeEditor(
    nodes=[
        ObjectTreeNode(
            node_for=[TutorialPath],
            label="nice_name",
            view=path_view
        ),
        ObjectTreeNode(
            node_for=[TutorialFile],
            label="nice_name",
            view=tutor_file_view
        ),
        ObjectTreeNode(
            node_for=[TutorialHTMLFile],
            label="nice_name",
            view=tutorial_html_view
        ),
        ObjectTreeNode(
            node_for=[TutorialTxtFile],
            label="nice_name",
            view=tutorial_text_view
        )
    ]
)


tutor_view = View(
    Item(
        name="root",
        show_label=False,
        editor=tutor_tree_editor,
    ),
    title="Tutorial",
    resizable=True,
    width=950,
    height=900,
)
