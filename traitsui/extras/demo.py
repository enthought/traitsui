#-------------------------------------------------------------------------
#
#  Copyright (c) 2005, Enthought, Inc.
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
#  Date:   09/15/2005
#
#-------------------------------------------------------------------------

""" A Traits UI demo that borrows heavily from the design of the wxPython demo.
"""

#-------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------

from __future__ import absolute_import

import sys
import glob
import token
import tokenize
import operator
from io import StringIO
import io
from configobj import ConfigObj

from traits.api import (HasTraits, HasPrivateTraits, Str, Instance, Property,
                        Any, Code, HTML, true, false, Dict)

from traitsui.api import (TreeEditor, ObjectTreeNode, TreeNodeObject, View,
                          Item, VSplit, Tabbed, VGroup, HGroup, Heading,
                          Handler, UIInfo, InstanceEditor, HTMLEditor, Include,
                          spring)

from os import listdir

from os.path import (join, isdir, split, splitext, dirname, basename, abspath,
                     exists, isabs)


#-------------------------------------------------------------------------
#  Global data:
#-------------------------------------------------------------------------

# Define the code used to populate the 'execfile' dictionary:
exec_str = """from traits.api import *

"""

#----------------------------------------------------------------------------
#  Return a 'user-friendly' name for a specified string:
#----------------------------------------------------------------------------


def user_name_for(name):
    name = name.replace('_', ' ')
    return name[:1].upper() + name[1:]

#-------------------------------------------------------------------------
#  Parses the contents of a specified source file into module comment and
#  source text:
#-------------------------------------------------------------------------


def extract_docstring_from_source(source):
    """Return module docstring and source code from python source code.

    Parameters
    ----------
    source : Str (Unicode)
        Python source code.

    Returns
    -------
    docstring : str
        The first module-level string; i.e. the module docstring.
    source : str
        The source code, sans docstring.
    """
    # Reset file and generate python tokens
    f = StringIO(source)
    python_tokens = tokenize.generate_tokens(f.readline)

    for ttype, tstring, tstart, tend, tline in python_tokens:
        token_name = token.tok_name[ttype]
        if token_name == 'STRING' and tstart[1] == 0:
            break
    else:
        # No docstrings found. Return blank docstring and all the source.
        return '', source.strip()

    source_lines = source.splitlines()

    # Extract module docstring lines and recombine
    docstring = eval('\n'.join(source_lines[tstart[0] - 1:tend[0]]))
    source_lines = source_lines[:tstart[0] - 1] + source_lines[tend[0]:]
    source = '\n'.join(source_lines)
    source = source.strip()

    return docstring, source


def parse_source(file_name):
    """Return module docstring and source code from python source file.

    Returns
    -------
    docstring : str
        The first module-level string; i.e. the module docstring.
    source : str
        The source code, sans docstring.
    """
    try:
        with io.open(file_name, 'r', encoding='utf-8') as fh:
            source_code = fh.read()
        return extract_docstring_from_source(source_code)
    except Exception:
        # Print an error message instead of failing silently.
        # Ideally, the message would be output to the "log" tab.
        import traceback
        traceback_text = traceback.format_exc()
        error_fmt = u"""Sorry, something went wrong.\n\n{}"""
        error_msg = error_fmt.format(traceback_text)
        return (error_msg, '')


#-------------------------------------------------------------------------
#  'DemoFileHandler' class:
#-------------------------------------------------------------------------

class DemoFileHandler(Handler):

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # The current 'info' object (for use by the 'write' method):
    info = Instance(UIInfo)

    #-------------------------------------------------------------------------
    #  Initializes the view:
    #-------------------------------------------------------------------------

    def init(self, info):
        # Save the reference to the current 'info' object:
        self.info = info

        # Set up the 'print' logger:
        df = info.object
        df.log = ''
        sys.stdout = sys.stderr = self

        # Read in the demo source file:
        df.description, df.source = parse_source(df.path)
        # Try to run the demo source file:

        # Append the path for the demo source file to sys.path, so as to
        # resolve any local (relative) imports in the demo source file.
        sys.path.append(dirname(df.path))

        locals = df.parent.init_dic
        locals['__name__'] = '___main___'
        locals['__file__'] = df.path
        sys.modules['__main__'].__file__ = df.path
        try:
            with io.open(df.path, 'r', encoding='utf-8') as fp:
                exec(compile(fp.read(), df.path, 'exec'), locals, locals)
            demo = self._get_object('modal_popup', locals)
            if demo is not None:
                demo = ModalDemoButton(demo=demo)
            else:
                demo = self._get_object('popup', locals)
                if demo is not None:
                    demo = DemoButton(demo=demo)
                else:
                    demo = self._get_object('demo', locals)
            # FIXME: If a 'demo' object could not be found, then try to execute
            # the file setting __name__ to __main__. A lot of test scripts have
            # the actual test running when __name__==__main__ and so we can at
            # least run all test examples this way. Use a do_later loop so as to
            # finish building the current UI before running the test.
            if demo is None:
                locals['__name__'] = '__main__'
                #do_later(self.execute_test, df, locals)
        except Exception as excp:
            demo = DemoError(msg=str(excp))

        # Clean up sys.path
        sys.path.remove(dirname(df.path))
        df.demo = demo

    def execute_test(self, df, locals):
        """ Executes the file in df.path in the namespace of locals."""
        with io.open(df.path, 'r', encoding='utf-8') as fp:
            exec(compile(fp.read(), df.path, 'exec'), locals, locals)

    #-------------------------------------------------------------------------
    #  Closes the view:
    #-------------------------------------------------------------------------

    def closed(self, info, is_ok):
        """ Closes the view.
        """
        info.object.demo = None

    #-------------------------------------------------------------------------
    #  Get a specified object from the execution dictionary:
    #-------------------------------------------------------------------------

    def _get_object(self, name, dic):
        object = dic.get(name) or dic.get(name.capitalize())
        if object is not None:
            if isinstance(type(object), type):
                try:
                    object = object()
                except:
                    pass

            if isinstance(object, HasTraits):
                return object

        return None

    #-------------------------------------------------------------------------
    #  Handles 'print' output:
    #-------------------------------------------------------------------------

    def write(self, text):
        self.info.object.log += text

    def flush(self):
        pass

# Create a singleton instance:
demo_file_handler = DemoFileHandler()

#-------------------------------------------------------------------------
#  'DemoError' class:
#-------------------------------------------------------------------------


class DemoError(HasPrivateTraits):

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # The error message text:
    msg = Code

    #-------------------------------------------------------------------------
    #  Traits view definitions:
    #-------------------------------------------------------------------------

    traits_view = View(
        VGroup(
            Heading('Error in source file'),
            Item('msg', style='custom', show_label=False),
        )
    )

#-------------------------------------------------------------------------
#  'DemoButton' class:
#-------------------------------------------------------------------------


class DemoButton(HasPrivateTraits):

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # The demo to be launched via a button:
    demo = Instance(HasTraits)

    # The demo view item to use:
    demo_item = Item('demo',
                     show_label=False,
                     editor=InstanceEditor(label='Run demo...', kind='live')
                     )

    #-------------------------------------------------------------------------
    #  Traits view definitions:
    #-------------------------------------------------------------------------

    traits_view = View(
        VGroup(
            VGroup(
                Heading('Click the button to run the demo:'),
                '20'
            ),
            HGroup(
                spring,
                Include('demo_item'),
                spring
            )
        ),
        resizable=True
    )

#-------------------------------------------------------------------------
#  'ModalDemoButton' class:
#-------------------------------------------------------------------------


class ModalDemoButton(DemoButton):

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # The demo view item to use:
    demo_item = Item('demo',
                     show_label=False,
                     editor=InstanceEditor(label='Run demo...', kind='modal')
                     )

#-------------------------------------------------------------------------
#  'DemoTreeNodeObject' class:
#-------------------------------------------------------------------------


class DemoTreeNodeObject(TreeNodeObject):

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Cached result of 'tno_has_children':
    _has_children = Any

    # Cached result of 'tno_get_children':
    _get_children = Any

    #-------------------------------------------------------------------------
    #  Returns whether chidren of this object are allowed or not:
    #-------------------------------------------------------------------------

    def tno_allows_children(self, node):
        """ Returns whether chidren of this object are allowed or not.
        """
        return self.allows_children

    #-------------------------------------------------------------------------
    #  Returns whether or not the object has children:
    #-------------------------------------------------------------------------

    def tno_has_children(self, node=None):
        """ Returns whether or not the object has children.
        """
        if self._has_children is None:
            self._has_children = self.has_children()

        return self._has_children

    #-------------------------------------------------------------------------
    #  Gets the object's children:
    #-------------------------------------------------------------------------

    def tno_get_children(self, node):
        """ Gets the object's children.
        """
        if self._get_children is None:
            self._get_children = self.get_children()

        return self._get_children

    #-------------------------------------------------------------------------
    #  Returns whether or not the object has children:
    #-------------------------------------------------------------------------

    def has_children(self, node):
        """ Returns whether or not the object has children.
        """
        raise NotImplementedError

    #-------------------------------------------------------------------------
    #  Gets the object's children:
    #-------------------------------------------------------------------------

    def get_children(self, node):
        """ Gets the object's children.
        """
        raise NotImplementedError

#-------------------------------------------------------------------------
#  'DemoFile' class:
#-------------------------------------------------------------------------


class DemoFile(DemoTreeNodeObject):

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Parent of this file:
    parent = Any

    # Name of file system path to this file:
    path = Property

    # Name of the file:
    name = Str

    # UI form of the 'name':
    nice_name = Property

    # Files don't allow children:
    allows_children = false

    # Description of what the demo does:
    description = HTML

    # Source code for the demo:
    source = Code

    # Demo object whose traits UI is to be displayed:
    demo = Instance(HasTraits)

    # Log of all print messages displayed:
    log = Code

    _nice_name = Str
    #-------------------------------------------------------------------------
    #  Implementation of the 'path' property:
    #-------------------------------------------------------------------------

    def _get_path(self):
        return join(self.parent.path, self.name + '.py')

    #-------------------------------------------------------------------------
    #  Implementation of the 'nice_name' property:
    #-------------------------------------------------------------------------

    def _get_nice_name(self):
        if not self._nice_name:
            self._nice_name = user_name_for(self.name)
        return self._nice_name

    def _set_nice_name(self, value):
        old = self.nice_name
        self._nice_name = value
        self.trait_property_changed('nice_name', old, value)

    #-------------------------------------------------------------------------
    #  Returns whether or not the object has children:
    #-------------------------------------------------------------------------

    def has_children(self):
        """ Returns whether or not the object has children.
        """
        return False

#-------------------------------------------------------------------------
#  'DemoPath' class:
#-------------------------------------------------------------------------


class DemoPath(DemoTreeNodeObject):

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Parent of this package:
    parent = Any

    # Name of file system path to this package:
    path = Property

    # Name of the directory:
    name = Str

    # UI form of the 'name':
    nice_name = Property

    # Description of the contents of the directory:
    description = Property(HTML)

    # Source code contained in the '__init__.py' file:
    source = Property(Code)

    # Dictionary containing symbols defined by the path's '__init__.py' file:
    init_dic = Property

    # Should .py files be included?
    use_files = true

    # Paths do allow children:
    allows_children = true

    # Configuration dictionary for this node
    # This trait is set when a config file exists for the parent of this path.
    config_dict = Dict

    # Configuration file for this node.
    config_filename = Str

    # Cached value of the nice_name property.
    _nice_name = Str

    #-------------------------------------------------------------------------
    #  Implementation of the 'path' property:
    #-------------------------------------------------------------------------

    def _get_path(self):
        return join(self.parent.path, self.name)

    #-------------------------------------------------------------------------
    #  Implementation of the 'nice_name' property:
    #-------------------------------------------------------------------------

    def _get_nice_name(self):
        if not self._nice_name:
            self._nice_name = user_name_for(self.name)
        return self._nice_name

    #-------------------------------------------------------------------------
    #  Setter for the 'nice_name' property:
    #-------------------------------------------------------------------------

    def _set_nice_name(self, value):
        old = self.nice_name
        self._nice_name = value
        self.trait_property_changed('nice_name', old, value)

    #-------------------------------------------------------------------------
    #  Implementation of the 'description' property:
    #-------------------------------------------------------------------------

    def _get_description(self):
        if self._description is None:
            self._get_init()

        return self._description

    #-------------------------------------------------------------------------
    #  Implementation of the 'source' property:
    #-------------------------------------------------------------------------

    def _get_source(self):
        if self._source is None:
            self._get_init()

        return self._source

    #-------------------------------------------------------------------------
    #  Implementation of the 'init_dic' property:
    #-------------------------------------------------------------------------

    def _get_init_dic(self):
        init_dic = {}
        description, source = parse_source(join(self.path, '__init__.py'))
        exec((exec_str + source), init_dic)
        return init_dic

        # fixme: The following code should work, but doesn't, so we use the
        #        preceding code instead. Changing any trait in the object in
        #        this method causes the tree to behave as if the DemoPath object
        #        had been selected instead of a DemoFile object. May be due to
        #        an 'anytrait' listener in the TreeEditor?
        #if self._init_dic is None:
        #   self._init_dic = {}
        #   #exec self.source in self._init_dic
        #return self._init_dic.copy()

    #-------------------------------------------------------------------------
    #  Initializes the description and source from the path's '__init__.py'
    #  file:
    #-------------------------------------------------------------------------

    def _get_init(self):
        if self.use_files:
            # Read in the '__init__.py' source file (if any):
            self._description, source = parse_source(
                join(self.path, '__init__.py'))
        else:
            self._description = ('<img src="traits_ui_demo.jpg">')
            source = ''

        self._source = exec_str + source

    #-------------------------------------------------------------------------
    #  Returns whether or not the object has children:
    #-------------------------------------------------------------------------

    def has_children(self):
        """ Returns whether or not the object has children.
        """
        path = self.path
        for name in listdir(path):
            cur_path = join(path, name)
            if isdir(cur_path):
                return True

            if self.use_files:
                name, ext = splitext(name)
                if (ext == '.py') and (name != '__init__'):
                    return True

        return False

    #-------------------------------------------------------------------------
    #  Gets the object's children:
    #-------------------------------------------------------------------------

    def get_children(self):
        """ Gets the object's children.
        """
        if self.config_dict or self.config_filename:
            children = self.get_children_from_config()
        else:
            children = self.get_children_from_datastructure()
        return children

    #-------------------------------------------------------------------------
    #  Gets the object's children based on the filesystem structure.
    #-------------------------------------------------------------------------
    def get_children_from_datastructure(self):
        """ Gets the object's children based on the filesystem structure.
        """

        dirs = []
        files = []
        path = self.path
        for name in listdir(path):
            cur_path = join(path, name)
            if isdir(cur_path):
                if self.has_py_files(cur_path):
                    dirs.append(DemoPath(parent=self, name=name))

            elif self.use_files:
                name, ext = splitext(name)
                if (ext == '.py') and (name != '__init__'):
                    files.append(DemoFile(parent=self, name=name))

        sort_key = operator.attrgetter('name')
        dirs.sort(key=sort_key)
        files.sort(key=sort_key)

        return (dirs + files)

    #-------------------------------------------------------------------------
    # Gets the object's children as specified in its configuration file or
    # dictionary.
    #-------------------------------------------------------------------------

    def get_children_from_config(self):
        """
        Gets the object's children as specified in its configuration file or
        dictionary.
        """

        if not self.config_dict:
            if exists(self.config_filename):
                try:
                    self.config_dict = ConfigObj(self.config_filename)
                except:
                    pass
        if not self.config_dict:
            return self.get_children_from_datastructure()

        dirs = []
        files = []
        for keyword, value in self.config_dict.items():
            if not value.get('no_demo'):
                sourcedir = value.pop('sourcedir', None)
                if sourcedir is not None:
                    # This is a demo directory.
                    demoobj = DemoPath(parent=self, name=sourcedir)
                    demoobj.nice_name = keyword
                    demoobj.config_dict = value
                    dirs.append(demoobj)
                else:
                    names = []
                    filenames = value.pop('files', [])
                    if not isinstance(filenames, list):
                        filenames = [filenames]
                    for filename in filenames:
                        filename = join(self.path, filename)
                        for name in glob.iglob(filename):
                            pathname, ext = splitext(name)
                            if (ext == '.py') and \
                                    (basename(pathname) != '__init__'):
                                names.append(pathname)
                    if len(names) > 1:
                        config_dict = {}
                        for name in names:
                            config_dict[basename(name)] = {'files':
                                                           name + '.py'}
                        demoobj = DemoPath(parent=self, name='')
                        demoobj.nice_name = keyword
                        demoobj.config_dict = config_dict
                        dirs.append(demoobj)
                    elif len(names) == 1:
                        file = DemoFile(parent=self, name=names[0])
                        file.nice_name = keyword
                        files.append(file)

        sort_key = operator.attrgetter('nice_name')
        dirs.sort(key=sort_key)
        files.sort(key=sort_key)

        return (dirs + files)

    #-------------------------------------------------------------------------
    #  Returns whether the specified path contains any .py files:
    #-------------------------------------------------------------------------

    def has_py_files(self, path):
        for name in listdir(path):
            cur_path = join(path, name)
            if isdir(cur_path):
                if self.has_py_files(cur_path):
                    return True

            else:
                name, ext = splitext(name)
                if ext == '.py':
                    return True

        return False

#-------------------------------------------------------------------------
#  Defines the demo tree editor:
#-------------------------------------------------------------------------

path_view = View(
    Tabbed(
        Item('description',
             label='Description',
             show_label=False,
             style='readonly',
             editor=HTMLEditor(format_text=True)
             ),
        Item('source',
             label='Source',
             show_label=False,
             style='custom'
             ),
        export='DockWindowShell',
        id='tabbed'
    ),
    id='traitsui.demos.demo.path_view',
    #dock    = 'horizontal'
)

demo_view = View(
    #VSplit(
    Tabbed(
        Item('description',
             label='Description',
             show_label=False,
             style='readonly',
             editor=HTMLEditor(format_text=True)
             ),
        Item('source',
             label='Source',
             show_label=False,
             style='custom'
             ),
        Item('demo',
             label='Demo',
             show_label=False,
             style='custom',
             resizable=True,
             # FIXME:
             # visible_when doesn't work correctly yet (for wx atleast)
             # for tabbed items. Needs more investigation.
                   visible_when='demo',
             ),
        Item('log',
             show_label=False,
             style='readonly'
             ),
        export='DockWindowShell',
        id='tabbed',
    ),
    # JDM moving log panel provisionally to its own tab, distracting here.
    #VGroup(
    #Item( 'log',
    #show_label = False,
    #style      = 'readonly'
    #),
    #label = 'Log'
    #),
    #export = 'DockWindowShell',
    #id     = 'vsplit'
    #),
    id='traitsui.demos.demo.file_view',
    #dock    = 'horizontal',
    handler=demo_file_handler
)

demo_tree_editor = TreeEditor(
    nodes=[
        ObjectTreeNode(node_for=[DemoPath],
                       label='nice_name',
                       view=path_view),
        ObjectTreeNode(node_for=[DemoFile],
                       label='nice_name',
                       view=demo_view)
    ]
)

#-------------------------------------------------------------------------
#  'Demo' class:
#-------------------------------------------------------------------------


class Demo(HasPrivateTraits):

    #-------------------------------------------------------------------------
    #  Trait definitions:
    #-------------------------------------------------------------------------

    # Path to the root demo directory:
    path = Str

    # Root path object for locating demo files:
    root = Instance(DemoPath)

    # Title for the demo
    title = Str

    #-------------------------------------------------------------------------
    #  Traits view definitions:
    #-------------------------------------------------------------------------

    def default_traits_view(self):
        """ Constructs the default traits view."""

        traits_view = View(
            Item(name='root',
                 id='root',
                 show_label=False,
                 editor=demo_tree_editor
                 ),
            title=self.title,
            id='traitsui.demos.demo.Demo',
            #dock      = 'horizontal',
            resizable=True,
            # JDM: Seems that QT interface does not deal well with these size
            # limits.
            # With them, we get repeated:
            #   Object::disconnect: Parentheses expected, signal AdvancedCodeWidget::lostFocus
            # But without them, it throws an exception on exit:
            #    Internal C++ object (_StickyDialog) already deleted.
            # No, actually sometimes we get the latter even with them.
            width=950,
            height=900
        )
        return traits_view

    #-------------------------------------------------------------------------
    #  Handles the 'root' trait being changed:
    #-------------------------------------------------------------------------

    def _root_changed(self, root):
        """ Handles the 'root' trait being changed.
        """
        root.parent = self

#-------------------------------------------------------------------------
#  Function to run the demo:
#-------------------------------------------------------------------------


def demo(use_files=False, dir_name=None, config_filename='',
         title='Traits UI Demos'):
    if dir_name is None:
        dir_name = dirname(abspath(sys.argv[0]))
    path, name = split(dir_name)
    if len(config_filename) > 0 and not isabs(config_filename):
        config_filename = join(path, name, config_filename)
    Demo(path=path,
         title=title,
         root=DemoPath(name=name,
                       use_files=use_files,
                       config_filename=config_filename)
         ).configure_traits()
