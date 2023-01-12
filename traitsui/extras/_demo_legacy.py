# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A Traits UI demo that borrows heavily from the design of the wxPython demo.

This copy of the demo application will only be maintained until ``ets-demo``
is released and distributed. This allows other ETS packages to continue to be
able to import the demo application until ``ets-demo`` is released.
(enthought/traitsui#950)
"""

import contextlib
import glob
from io import StringIO
import operator
import os
from os import listdir
from os.path import (
    abspath,
    basename,
    dirname,
    exists,
    isabs,
    isdir,
    join,
    split,
    splitext,
)
import sys
import token
import tokenize
import traceback


from configobj import ConfigObj

from pyface.api import ImageResource
from traits.api import (
    Any,
    Bool,
    Button,
    cached_property,
    Code,
    Dict,
    HasPrivateTraits,
    HasTraits,
    HTML,
    Instance,
    Property,
    Str,
)
from traitsui.api import (
    Action,
    CodeEditor,
    Handler,
    Heading,
    HGroup,
    HSplit,
    HTMLEditor,
    Include,
    InstanceEditor,
    Item,
    ModelView,
    ObjectTreeNode,
    ShellEditor,
    spring,
    Tabbed,
    ToolBar,
    TreeEditor,
    TreeNodeObject,
    UIInfo,
    UItem,
    VGroup,
    View,
    VSplit,
)


# -------------------------------------------------------------------------
#  Global data:
# -------------------------------------------------------------------------

# Define the code used to populate the 'execfile' dictionary:
exec_str = """from traits.api import *

"""

# The name of the file being looked up for the description of a directory
DESCRIPTION_RST_FILENAME = "index.rst"

# ----------------------------------------------------------------------------
#  Return a 'user-friendly' name for a specified string:
# ----------------------------------------------------------------------------


def user_name_for(name):
    name = name.replace("_", " ")
    return name[:1].upper() + name[1:]


# -------------------------------------------------------------------------
#  Parses the contents of a specified source file into module comment and
#  source text:
# -------------------------------------------------------------------------


def extract_docstring_from_source(source):
    """Return module docstring and source code from python source code.

    Parameters
    ----------
    source : Str
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
        if token_name == "STRING" and tstart[1] == 0:
            break
    else:
        # No docstrings found. Return blank docstring and all the source.
        return "", source.strip()

    source_lines = source.splitlines()

    # Extract module docstring lines and recombine
    docstring = eval("\n".join(source_lines[tstart[0] - 1 : tend[0]]))
    source_lines = source_lines[: tstart[0] - 1] + source_lines[tend[0] :]
    source = "\n".join(source_lines)
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
        source_code = _read_file(file_name)
        return extract_docstring_from_source(source_code)
    except Exception:
        # Print an error message instead of failing silently.
        # Ideally, the message would be output to the "log" tab.
        traceback_text = traceback.format_exc()
        error_fmt = """Sorry, something went wrong.\n\n{}"""
        error_msg = error_fmt.format(traceback_text)
        return (error_msg, "")


def _read_file(path, mode='r', encoding='utf8'):
    """Returns the contents of a specified text file."""
    with open(path, mode, encoding=encoding) as fh:
        result = fh.read()
    return result


# -------------------------------------------------------------------------
#  'DemoFileHandler' class:
# -------------------------------------------------------------------------


@contextlib.contextmanager
def _set_stdout(std_out):
    stdout, stderr = sys.stdout, sys.stderr
    try:
        sys.stdout = sys.stderr = std_out
        yield std_out
    finally:
        sys.stdout, sys.stderr = stdout, stderr


class DemoFileHandler(Handler):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Run the demo file
    run_button = Button(image=ImageResource("run"), label="Run")

    #: The current 'info' object (for use by the 'write' method):
    info = Instance(UIInfo)

    def _run_button_changed(self):
        demo_file = self.info.object
        with _set_stdout(self):
            demo_file.run_code()

    def init(self, info):
        # Save the reference to the current 'info' object:
        self.info = info
        demo_file = info.object
        with _set_stdout(self):
            demo_file.init()
        return True

    def closed(self, info, is_ok):
        """Closes the view."""
        demo_file = info.object
        if hasattr(demo_file, 'demo'):
            demo_file.demo = None

    # -------------------------------------------------------------------------
    #  Handles 'print' output:
    # -------------------------------------------------------------------------

    def write(self, text):
        demo_file = self.info.object
        demo_file.log += text

    def flush(self):
        pass


# Create a singleton instance:
demo_file_handler = DemoFileHandler()


class DemoError(HasPrivateTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The error message text:
    msg = Code()

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    traits_view = View(
        VGroup(
            Heading("Error in source file"),
            Item("msg", style="custom", show_label=False),
        )
    )


class DemoButton(HasPrivateTraits):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The demo to be launched via a button:
    demo = Instance(HasTraits)

    #: The demo view item to use:
    demo_item = Item(
        "demo",
        show_label=False,
        editor=InstanceEditor(label="Run demo...", kind="live"),
    )

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    traits_view = View(
        VGroup(
            VGroup(Heading("Click the button to run the demo:"), "20"),
            HGroup(spring, Include("demo_item"), spring),
        ),
        resizable=True,
    )


class ModalDemoButton(DemoButton):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: The demo view item to use:
    demo_item = Item(
        "demo",
        show_label=False,
        editor=InstanceEditor(label="Run demo...", kind="modal"),
    )


class DemoTreeNodeObject(TreeNodeObject):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Cached result of 'tno_has_children':
    _has_children = Any()

    #: Cached result of 'tno_get_children':
    _get_children = Any()

    # -------------------------------------------------------------------------
    #  Returns whether chidren of this object are allowed or not:
    # -------------------------------------------------------------------------

    def tno_allows_children(self, node):
        """Returns whether chidren of this object are allowed or not."""
        return self.allows_children

    # -------------------------------------------------------------------------
    #  Returns whether or not the object has children:
    # -------------------------------------------------------------------------

    def tno_has_children(self, node=None):
        """Returns whether or not the object has children."""
        if self._has_children is None:
            self._has_children = self.has_children()

        return self._has_children

    # -------------------------------------------------------------------------
    #  Gets the object's children:
    # -------------------------------------------------------------------------

    def tno_get_children(self, node):
        """Gets the object's children."""
        if self._get_children is None:
            self._get_children = self.get_children()

        return self._get_children

    # -------------------------------------------------------------------------
    #  Returns whether or not the object has children:
    # -------------------------------------------------------------------------

    def has_children(self, node):
        """Returns whether or not the object has children."""
        raise NotImplementedError

    # -------------------------------------------------------------------------
    #  Gets the object's children:
    # -------------------------------------------------------------------------

    def get_children(self):
        """Gets the object's children."""
        raise NotImplementedError


class DemoFileBase(DemoTreeNodeObject):
    #: Parent of this file:
    parent = Any()

    #: Name of file system path to this file:
    path = Property(observe='parent.path,name')

    #: Name of the file:
    name = Str()

    #: UI form of the 'name':
    nice_name = Property()

    #: Files don't allow children:
    allows_children = Bool(False)

    #: Description of what the demo does:
    description = HTML()

    #: The base URL for links:
    base_url = Property(observe='path')

    #: The css file for this node.
    css_filename = Str("default.css")

    #: Log of all print messages displayed:
    log = Code()

    _nice_name = Str()

    def init(self):
        self.log = ""

    # -------------------------------------------------------------------------
    #  Implementation of the 'path' property:
    # -------------------------------------------------------------------------

    def _get_path(self):
        return join(self.parent.path, self.name)

    def _get_base_url(self):
        if isdir(self.path):
            base_dir = self.path
        else:
            base_dir = dirname(self.path)
        return base_dir

    # -------------------------------------------------------------------------
    #  Implementation of the 'nice_name' property:
    # -------------------------------------------------------------------------

    def _get_nice_name(self):
        if not self._nice_name:
            name, ext = splitext(self.name)
            self._nice_name = user_name_for(name)
        return self._nice_name

    def _set_nice_name(self, value):
        old = self.nice_name
        self._nice_name = value
        self.trait_property_changed("nice_name", old, value)

    # -------------------------------------------------------------------------
    #  Returns whether or not the object has children:
    # -------------------------------------------------------------------------

    def has_children(self):
        """Returns whether or not the object has children."""
        return False

    def get_children(self):
        """Gets the demo file's children."""
        return []


class DemoFile(DemoFileBase):

    #: Source code for the demo:
    source = Code()

    #: Demo object whose traits UI is to be displayed:
    demo = Instance(HasTraits)

    #: Local namespace for executed code:
    locals = Dict(Str, Any)

    def init(self):
        super().init()
        description, source = parse_source(self.path)
        self.description = publish_html_str(description, self.css_filename)
        self.source = source
        self.run_code()

    def run_code(self):
        """Runs the code associated with this demo file."""
        try:
            # Get the execution context dictionary:
            locals = self.parent.init_dic
            locals["__name__"] = "___main___"
            locals["__file__"] = self.path
            sys.modules["__main__"].__file__ = self.path

            exec(self.source, locals, locals)

            demo = self._get_object("modal_popup", locals)
            if demo is not None:
                demo = ModalDemoButton(demo=demo)
            else:
                demo = self._get_object("popup", locals)
                if demo is not None:
                    demo = DemoButton(demo=demo)
                else:
                    demo = self._get_object("demo", locals)
        except Exception:
            traceback.print_exc()
        else:
            self.demo = demo
        self.locals = locals

    # -------------------------------------------------------------------------
    #  Get a specified object from the execution dictionary:
    # -------------------------------------------------------------------------

    def _get_object(self, name, dic):
        object = dic.get(name) or dic.get(name.capitalize())
        if object is not None:
            if isinstance(type(object), type):
                try:
                    object = object()
                except Exception:
                    pass

            if isinstance(object, HasTraits):
                return object

        return None


# HTML template for displaying an image file:
_image_template = """<html>
<head>
<link rel="stylesheet" type="text/css" href="{}">
</head>
<body>
<img src="{}">
</body>
</html>
"""


class DemoContentFile(DemoFileBase):
    def init(self):
        super().init()
        file_str = _read_file(self.path)
        self.description = publish_html_str(file_str, self.css_filename)


class DemoImageFile(DemoFileBase):
    def init(self):
        super().init()
        self.description = _image_template.format(self.css_filename, self.path)


class DemoPath(DemoTreeNodeObject):
    """This class represents a directory."""

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Parent of this package:
    parent = Any()

    #: Name of file system path to this package:
    path = Property(observe='parent.path,name')

    #: Description of what the demo does:
    description = Property(HTML, observe="path,css_filename")

    #: The base URL for links:
    base_url = Property(observe='path')

    #: The css file for this node.
    css_filename = Str("default.css")

    #: Name of the directory:
    name = Str()

    #: UI form of the 'name':
    nice_name = Property()

    #: Dictionary containing symbols defined by the path's '__init__.py' file:
    init_dic = Property()

    #: Should .py files be included?
    use_files = Bool(True)

    #: Paths do allow children:
    allows_children = Bool(True)

    #: Configuration dictionary for this node
    #: This trait is set when a config file exists for the parent of this path.
    config_dict = Dict()

    #: Configuration file for this node.
    config_filename = Str()

    #: The css file for this node.
    css_filename = Str("default.css")

    #: Shadow trait for description property
    _description = Str()

    #: Cached value of the nice_name property.
    _nice_name = Str()

    #: Dictionary mapping file extensions to callables
    _file_factory = Dict()

    def __file_factory_default(self):
        return {
            ".htm": DemoContentFile,
            ".html": DemoContentFile,
            ".jpeg": DemoImageFile,
            ".jpg": DemoImageFile,
            ".png": DemoImageFile,
            ".py": DemoFile,
            ".rst": DemoContentFile,
            ".txt": DemoContentFile,
        }

    # -------------------------------------------------------------------------
    #  Implementation of the 'path' property:
    # -------------------------------------------------------------------------

    def _get_path(self):
        if self.parent is not None:
            path = join(self.parent.path, self.name)
        else:
            path = self.name

        return path

    def _get_base_url(self):
        if isdir(self.path):
            base_dir = self.path
        else:
            base_dir = dirname(self.path)
        return base_dir

    # -------------------------------------------------------------------------
    #  Implementation of the 'nice_name' property:
    # -------------------------------------------------------------------------

    def _get_nice_name(self):
        if not self._nice_name:
            self._nice_name = user_name_for(self.name)
        return self._nice_name

    # -------------------------------------------------------------------------
    #  Setter for the 'nice_name' property:
    # -------------------------------------------------------------------------

    def _set_nice_name(self, value):
        old = self.nice_name
        self._nice_name = value
        self.trait_property_changed("nice_name", old, value)

    # -------------------------------------------------------------------------
    #  Implementation of the 'description' property:
    # -------------------------------------------------------------------------

    @cached_property
    def _get_description(self):
        index_rst = os.path.join(self.path, DESCRIPTION_RST_FILENAME)
        if os.path.exists(index_rst):
            with open(index_rst, "r", encoding="utf-8") as f:
                description = f.read()
        else:
            description = ""

        if self.css_filename:
            result = publish_html_str(description, self.css_filename)
        else:
            result = publish_html_str(description)
        return result

    # -------------------------------------------------------------------------
    #  Implementation of the 'init_dic' property:
    # -------------------------------------------------------------------------

    def _get_init_dic(self):
        init_dic = {}
        description, source = parse_source(join(self.path, "__init__.py"))
        exec((exec_str + source), init_dic)
        return init_dic

    # -------------------------------------------------------------------------
    #  Returns whether or not the object has children:
    # -------------------------------------------------------------------------

    def has_children(self):
        """Returns whether or not the object has children."""
        path = self.path
        for name in listdir(path):
            cur_path = join(path, name)
            if isdir(cur_path):
                return True

            if self.use_files:
                name, ext = splitext(name)
                if (ext == ".py") and (name != "__init__"):
                    return True
                elif ext in self._file_factory:
                    return True

        return False

    # -------------------------------------------------------------------------
    #  Gets the object's children:
    # -------------------------------------------------------------------------

    def get_children(self):
        """Gets the object's children."""
        if self.config_dict or self.config_filename:
            children = self.get_children_from_config()
        else:
            children = self.get_children_from_datastructure()
        return children

    # -------------------------------------------------------------------------
    #  Gets the object's children based on the filesystem structure.
    # -------------------------------------------------------------------------
    def get_children_from_datastructure(self):
        """Gets the object's children based on the filesystem structure."""

        dirs = []
        files = []
        path = self.path
        for name in listdir(path):
            cur_path = join(path, name)
            if isdir(cur_path):
                if self.has_py_files(cur_path):
                    dirs.append(
                        DemoPath(
                            parent=self,
                            name=name,
                            css_filename=join('..', self.css_filename),
                        )
                    )
            elif self.use_files:
                if name != "__init__.py":
                    try:
                        demo_file = self._handle_file(name)
                        demo_file.css_filename = self.css_filename
                        files.append(demo_file)
                    except KeyError:
                        pass

        sort_key = operator.attrgetter("name")
        dirs.sort(key=sort_key)
        files.sort(key=sort_key)

        return dirs + files

    # -------------------------------------------------------------------------
    # Gets the object's children as specified in its configuration file or
    # dictionary.
    # -------------------------------------------------------------------------

    def get_children_from_config(self):
        """
        Gets the object's children as specified in its configuration file or
        dictionary.
        """

        if not self.config_dict:
            if exists(self.config_filename):
                try:
                    self.config_dict = ConfigObj(self.config_filename)
                except Exception:
                    pass
        if not self.config_dict:
            return self.get_children_from_datastructure()

        dirs = []
        files = []
        for keyword, value in self.config_dict.items():
            if not value.get("no_demo"):
                sourcedir = value.pop("sourcedir", None)
                if sourcedir is not None:
                    # This is a demo directory.
                    demoobj = DemoPath(
                        parent=self,
                        name=sourcedir,
                        css_filename=join("..", self.css_filename),
                    )
                    demoobj.nice_name = keyword
                    demoobj.config_dict = value
                    dirs.append(demoobj)
                else:
                    names = []
                    filenames = value.pop("files", [])
                    if not isinstance(filenames, list):
                        filenames = [filenames]
                    for filename in filenames:
                        filename = join(self.path, filename)
                        for name in glob.iglob(filename):
                            if basename(name) != "__init__.py":
                                names.append(name)
                    if len(names) > 1:
                        config_dict = {}
                        for name in names:
                            config_dict[basename(name)] = {"files": name}
                        demoobj = DemoPath(parent=self, name="")
                        demoobj.nice_name = keyword
                        demoobj.config_dict = config_dict
                        demoobj.css_filename = os.path.join(
                            "..", self.css_filename
                        )
                        dirs.append(demoobj)
                    elif len(names) == 1:
                        try:
                            demo_file = self._handle_file(name)
                            files.append(demo_file)
                            demo_file.css_filename = self.css_filename
                        except KeyError:
                            pass

        sort_key = operator.attrgetter("nice_name")
        dirs.sort(key=sort_key)
        files.sort(key=sort_key)

        return dirs + files

    # -------------------------------------------------------------------------
    #  Returns whether the specified path contains any .py files:
    # -------------------------------------------------------------------------

    def has_py_files(self, path):
        for name in listdir(path):
            cur_path = join(path, name)
            if isdir(cur_path):
                if self.has_py_files(cur_path):
                    return True

            else:
                name, ext = splitext(name)
                if ext == ".py":
                    return True

        return False

    def _handle_file(self, filename):
        """Process a file based on its extension."""
        _, ext = splitext(filename)
        file_factory = self._file_factory[ext]
        demo_file = file_factory(parent=self, name=filename)
        return demo_file


# -------------------------------------------------------------------------
#  Defines the demo tree editor:
# -------------------------------------------------------------------------

demo_path_view = View(
    UItem(
        "description",
        style="readonly",
        editor=HTMLEditor(
            format_text=True,
            base_url_name='base_url',
        ),
    ),
    id="demo_path_view",
    kind='subpanel',
)

demo_file_view = View(
    HSplit(
        UItem(
            "description",
            style="readonly",
            editor=HTMLEditor(
                format_text=True,
                base_url_name='base_url',
            ),
        ),
        VSplit(
            VGroup(
                UItem("source", style="custom"),
                HGroup(
                    spring,
                    UItem(
                        "handler.run_button",
                    ),
                    visible_when="source is not None",
                ),
            ),
            Tabbed(
                Item(
                    "log",
                    style="readonly",
                    editor=CodeEditor(
                        show_line_numbers=False, selected_color=0xFFFFFF
                    ),
                    label="Output",
                    show_label=False,
                ),
                Item(
                    "locals",
                    editor=ShellEditor(share=True),
                    label="Shell",
                    show_label=False,
                ),
                UItem(
                    "demo",
                    style="custom",
                    resizable=True,
                ),
            ),
            dock="horizontal",
        ),
    ),
    id="demo_file_view",
    handler=demo_file_handler,
    kind='subpanel',
)

demo_content_view = View(
    Tabbed(
        UItem(
            "description",
            style="readonly",
            editor=HTMLEditor(
                format_text=True,
                base_url_name='base_url',
            ),
        ),
    ),
    handler=demo_file_handler,
    kind='subpanel',
)


demo_tree_editor = TreeEditor(
    nodes=[
        ObjectTreeNode(
            node_for=[DemoPath],
            label="nice_name",
            view=demo_path_view,
        ),
        ObjectTreeNode(
            node_for=[DemoFile], label="nice_name", view=demo_file_view
        ),
        ObjectTreeNode(
            node_for=[DemoContentFile],
            label="nice_name",
            view=demo_content_view,
        ),
        ObjectTreeNode(
            node_for=[DemoImageFile], label="nice_name", view=demo_content_view
        ),
    ],
    selected='selected_node',
)


next_tool = Action(
    name='Next',
    image=ImageResource("next"),
    tooltip="Go to next file",
    action="do_next",
    enabled_when="_next_node is not None",
)

previous_tool = Action(
    name='Previous',
    image=ImageResource("previous"),
    tooltip="Go to next file",
    action="do_previous",
    enabled_when="_previous_node is not None",
)

parent_tool = Action(
    name='Parent',
    image=ImageResource("parent"),
    tooltip="Go to next file",
    action="do_parent",
    enabled_when="(selected_node is not None) and "
    "(object.selected_node.parent is not None)",
)


class Demo(ModelView):

    #: Root path object for locating demo files:
    model = Instance(DemoPath)

    #: Path to the root demo directory:
    path = Str()

    #: Selected node of the demo path tree.
    selected_node = Any()

    #: Title for the demo
    title = Str()

    _next_node = Property()

    _previous_node = Property()

    def do_next(self, event=None):
        self.selected_node = self._next_node

    def do_previous(self, event=None):
        self.selected_node = self._previous_node

    def do_parent(self, event=None):
        if self.selected_node is not None:
            parent = self.selected_node.parent
            self.selected_node = parent

    def init(self, info):
        info.ui.title = self.title
        return True

    def _get__next_node(self):
        next = None
        node = self.selected_node
        children = node.tno_get_children(node)

        if len(children) > 0:
            next = children[0]
        else:
            parent = node.parent
            while parent is not None:
                siblings = parent.tno_get_children(parent)
                index = siblings.index(node)
                if index < (len(siblings) - 1):
                    next = siblings[index + 1]
                    break

                parent, node = parent.parent, parent

        return next

    def _get__previous_node(self):
        previous = None
        node = self.selected_node
        parent = node.parent
        if parent is not None:
            siblings = parent.tno_get_children(parent)
            index = siblings.index(node)
            if index > 0:
                previous = siblings[index - 1]
                previous_children = previous.tno_get_children(previous)
                while len(previous_children) > 0:
                    previous = previous_children[-1]
                    previous_children = previous.tno_get_children(previous)
            else:
                previous = parent

        return previous

    # -------------------------------------------------------------------------
    #  Traits view definitions:
    # -------------------------------------------------------------------------

    def default_traits_view(self):
        # XXX need to do this to hide the instantiation of ToolBar from null
        # toolkit tests.  It would be preferable to have this be declarative.
        return View(
            Item(
                name="model",
                id="model",
                show_label=False,
                editor=demo_tree_editor,
            ),
            id="traitsui.demos.demo.Demo",
            toolbar=ToolBar(
                previous_tool, parent_tool, next_tool, show_tool_names=True
            ),
            resizable=True,
            width=1200,
            height=700,
        )


# -------------------------------------------------------------------------
#  Utilities to convert rst strings/files to html.
# -------------------------------------------------------------------------


def _get_settings(css_path=None):
    """Helper function to make settings dictionary
    consumable by docutils

    Parameters
    ----------
    css_path: string or None (default)
        If not None, use the CSS stylesheet.

    Returns
    -------
    dict
    """
    settings = {'output_encoding': 'unicode'}
    if css_path is not None:
        settings['stylesheet_path'] = css_path
        settings['embed_stylesheet'] = False
        settings['stylesheet'] = None

    return settings


def publish_html_str(rst_str, css_path=None):
    """Format RST string to html using `docutils` if available.
    Otherwise, return the input `rst_str`.

    Parameters
    ----------
    rst_str: string
        reStructuredText

    css_path: string or None (default)
        If not None, use the CSS stylesheet.

    Returns
    -------
    string
    """
    try:
        from docutils.core import publish_string
    except Exception:
        return rst_str

    settings = _get_settings(css_path)
    return publish_string(
        rst_str, writer_name='html', settings_overrides=settings
    )


def publish_html_file(rst_file_path, html_out_path, css_path=None):
    """Format reStructuredText in `rst_file_path` to html using `docutils`
    if available. Otherwise, does nothing.

    Parameters
    ----------
    rst_file_path: string

    html_out_path: string

    css_path: string or None (default)
        If not None, use the CSS stylesheet.

    Returns
    -------
    None
    """
    try:
        from docutils.core import publish_file
    except Exception:
        return

    settings = _get_settings(css_path)
    publish_file(
        source_path=rst_file_path,
        destination_path=html_out_path,
        writer_name='html',
        settings_overrides=settings,
    )


# -------------------------------------------------------------------------
#  Function to run the demo:
# -------------------------------------------------------------------------


def demo(
    use_files=False,
    dir_name=None,
    config_filename="",
    title="Traits UI Demos",
    css_filename="default.css",
):
    if dir_name is None:
        dir_name = dirname(abspath(sys.argv[0]))
    path, name = split(dir_name)
    if len(config_filename) > 0 and not isabs(config_filename):
        config_filename = join(path, name, config_filename)
    Demo(
        path=path,
        title=title,
        model=DemoPath(
            name=dir_name,
            nice_name=user_name_for(name),
            use_files=use_files,
            config_filename=config_filename,
            css_filename=css_filename,
        ),
    ).configure_traits()
