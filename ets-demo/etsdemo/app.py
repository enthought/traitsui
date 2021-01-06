# (C) Copyright 2020 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

""" A Traits UI demo that borrows heavily from the design of the wxPython demo.
"""

import abc
import contextlib
import glob
import io
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
import subprocess
import tempfile
import token
import tokenize
import traceback
import types

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
    List,
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
    docstring = eval("\n".join(source_lines[tstart[0] - 1: tend[0]]))
    source_lines = source_lines[: tstart[0] - 1] + source_lines[tend[0]:]
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
    """ Returns the contents of a specified text file.
    """
    with open(path, mode, encoding=encoding) as fh:
        result = fh.read()
    return result


# -------------------------------------------------------------------------
#  'DemoFileHandler' class:
# -------------------------------------------------------------------------


class _TempSysPath:
    """ Temporarily prepend the directory containing the provided script
    to sys.path.
    """

    def __init__(self, script_file_path):
        self._path = os.path.dirname(os.fspath(script_file_path))

    def __enter__(self):
        sys.path.insert(0, self._path)
        return self

    def __exit__(self, *args):
        try:
            sys.path.remove(self._path)
        except ValueError:
            pass


class _TempModule:
    """Temporarily replace a module in sys.modules with an empty namespace.

    Parameters
    ----------
    mod_name : str
        Name of the module to be replaced (if exists) or created (if absent).
    """
    def __init__(self, mod_name):
        self.mod_name = mod_name
        self.module = types.ModuleType(mod_name)
        self._saved_module = []

    def __enter__(self):
        try:
            self._saved_module.append(sys.modules[self.mod_name])
        except KeyError:
            pass
        sys.modules[self.mod_name] = self.module
        return self

    def __exit__(self, *args):
        if self._saved_module:
            sys.modules[self.mod_name] = self._saved_module[0]
        else:
            del sys.modules[self.mod_name]
        self._saved_module = []


class _CloseNewGui:
    """ Context manager to close any top level windows that were absent
    when the context was entered.

    Strong references to the top-level windows are held upon entering the
    context, and are released when the context is exited.
    """

    # FIXME: For other toolkit backend (i.e. wx), this context manager
    # may have to do nothing. Note that the application currently does not
    # run well on wx at all.

    def __enter__(self):
        from pyface.qt import QtGui
        app = QtGui.QApplication.instance()
        self.existing_windows = app.topLevelWidgets()
        return self

    def __exit__(self, *args):
        try:
            from pyface.qt import QtGui
            app = QtGui.QApplication.instance()
            for window in app.topLevelWidgets():
                if window not in self.existing_windows:
                    window.close()
        finally:
            self.existing_windows = []


class CodeRunnerBase(abc.ABC):
    """ Abstract base class to define an interface used for running local code.
    """

    @property
    @abc.abstractmethod
    def locals(self):
        """ Namespace for the executed code.

        Default implementation provides an empty namespace.
        """
        return {}

    @abc.abstractmethod
    def start(self, code, script_name, init_globals, stdout, stderr):
        """ Start the runner to run the code as main.

        Default implementation does nothing.

        Parameters
        ----------
        code : str
            Code to be executed as main. An empty module namespace will be
            created to replace __main__ temporarily until the runner is
            stopped.
        script_name : str
            Path to be set as __file__.
        init_globals : dict
            Initial namespace variables.
        stdout : file-like
            File-like object for redirecting STDOUT when the code is executed.
        stderr : file-like
            File-like object for redirecting STDERR when the code is executed.

        Raises
        ------
        RuntimeError
            If the runner has already started.
        """
        pass

    @abc.abstractmethod
    def stop(self):
        """ Stop the runner and cleanup.
        If the runner has not started, do nothing.

        Default implementation does nothing.
        """
        pass


class SubprocessCodeRunner(CodeRunnerBase):
    """ A runner for running code in a subprocess.

    Support:
    - Relative import works as expected, with no risk of name shadowing.
    - Discovery of resources using __file__ works as expected, but this
      breaks __doc__, see limitations.
    - Stopping the runner will close any new GUI window left open since the
      runner starts, because the subprocess is forced killed.

    Known limtations:
    - STDOUT and STDERR are not redirected. Hence there are currently no
      error feedback mechanism. i.e. The "Output" tab in the GUI is basically
      non-functional.
    - No initial global variables can be provided. i.e. The "Shell" tab in the
      GUI is basically non-functional.
      (Note this is an existing feature of the demo application to incorporate
      variables defined in the __init__.py in the same folder, but this feature
      may not be used by any examples. Running a script directly without the -m
      switch does not execute __init__.py.)
    - Access to interact with the namespace from the executed code is not
      available (i.e. the Python shell feature is not supported).
    - Attempt is made to patch __file__, but currently this breaks implicit
      assignment of __doc__ using module level docstring.
    - Risk of leaving orphant subprocess around if forcing killing them upon
      stopping the runner was not successful?
    """

    def __init__(self):
        self._started = False
        self._exit_stack = contextlib.ExitStack()

    @property
    def locals(self):
        """ Empty namespace.
        """
        return {}

    def start(self, code, script_name, init_globals, stdout, stderr):
        """ Reimplemented CodeRunnerBase.start

        init_globals is not used. A warning is emitted if it is provided.

        stdout and stderr are not used either.
        """
        self._started = True

        # Write the modified code to a temporary script file.
        # Patch __file__ in-place for resources management
        # but this breaks __doc__ for the HTMLEditor example!
        tmp_dir = self._exit_stack.enter_context(
            tempfile.TemporaryDirectory()
        )
        tmp_script_name = os.path.join(tmp_dir, "tmp.py")
        with open(tmp_script_name, "w", encoding="utf-8") as fp:
            fp.write(f"__file__ = {script_name!r}\n")
            fp.write(code)

        # Set PYTHONPATH to support local import in the examples.
        python_path = os.path.dirname(script_name)
        existing_path = os.environ.get("PYTHONPATH")
        if existing_path is not None:
            python_path += os.pathsep + existing_path

        # Run the script in a separate process...
        # FIXME: STDOUT/STDERR needs to be consumed and be made visible
        # in the application.
        process = subprocess.Popen(
            [sys.executable, tmp_script_name],
            env=dict(os.environ, PYTHONPATH=python_path),
            encoding="utf-8",
        )

        def kill_process(*args):
            process.kill()

        self._exit_stack.push(process.__exit__)
        self._exit_stack.push(kill_process)

    def stop(self):
        """ Reimplemented CodeRunnerBase.stop
        """
        if not self._started:
            return

        self._exit_stack.close()
        self._started = False


class LocalCodeRunner(CodeRunnerBase):
    """ Runner to execute arbitrary code as main.

    Support:
    - Relative import works as expected (except name shadowing may occur, see
      limitations).
    - Initial global variables can be provided.
      (Note this is an existing feature of the demo application to incorporate
      variables defined in the __init__.py in the same folder, but this feature
      may not be used by any examples. Running a script directly without the -m
      switch does not execute __init__.py.)
    - STDOUT/STDERR are redirected to be visible in the demo application (but
      only briefly, see limitations).
    - Stopping the runner will close any new GUI window left open since the
      runner starts.
    - Namespace variables from the executed code can be interacted with
      directly.

    Known limitations:
    - Redirection of STDOUT/STDERR are restored when the code executed returns.
      This means any new content in STDOUT/STDERR triggered by deferred actions
      (e.g. GUI interaction) are not redirected. This is an existing limitation
      of the demo application.
    - Fatal exception (e.g. qFatal from Qt) arising from the given code is not
      isolated from the process running this runner, hence it could bring down
      the demo application.
    - Although the __main__ module is restored after the runner is stopped,
      any import cache created upon executing the given code is not
      invalidated. This could result in strange interaction if the runner
      is run again with code refering to a module under the same name assuming
      a different import finder path (i.e. name shadowing and double import).
    """

    def __init__(self):
        self._started = False
        self._exit_stack = contextlib.ExitStack()
        self._locals = {}

    @property
    def locals(self):
        """ Namespace for the executed code.
        """
        return self._locals

    def start(self, code, script_name, init_globals, stdout, stderr):
        """ Reimplemented CodeRunnerBase.start

        The namespace created by executing the code can be retrieved via
        the ``locals`` property.

        After the runner has started, the sys.module['__main__'] is replaced
        with the module created for the given code. The original __main__
        module will be restored when the runner stops.
        """
        if self._started:
            raise RuntimeError("The runner has already started.")

        self._started = True

        mod_name = "__main__"
        temp_module_manager = _TempModule(mod_name)
        run_globals = temp_module_manager.module.__dict__
        run_globals.update(init_globals)
        run_globals.update(
            __name__=mod_name,
            __file__=script_name,
            __cached__=None,
            __loader__=None,
            __package__=None,
            __spec__=None,
        )
        # These contexts span the runner's start-to-stop scope. They support
        # deferred GUI interactions that trigger local imports or local
        # discovery of files.
        with contextlib.ExitStack() as stack:
            stack.enter_context(temp_module_manager)
            stack.enter_context(_TempSysPath(script_name))
            stack.enter_context(_CloseNewGui())
            self._exit_stack = stack.pop_all()

        # limit the scope for redirecting stdout/stderr to just this
        # initial execution, otherwise the redirection may intefere
        # with the operation of the demo application.
        # FIXME: sys.argv _may_ need modification too.
        with contextlib.redirect_stdout(stdout), \
                contextlib.redirect_stderr(stderr):
            try:
                exec(code, run_globals)
            except Exception:
                traceback.print_exc(file=stderr)
            else:
                self._locals = run_globals

    def stop(self):
        """ Stop the runner and cleanup.
        If the runner has not started, do nothing.
        """
        if not self._started:
            return

        self._locals = {}
        self._exit_stack.close()
        self._started = False


class _StreamMock(io.IOBase):
    """ A file-like object that redirects write operation to a given callable.

    Useful to redirecting content intended to be written to a io stream
    (e.g. STDOUT and STDERR) to anything.

    Parameters
    ----------
    writer : callable(str)
        Callable to handle the given string.
    """

    def __init__(self, writer):
        self.writer = writer

    def write(self, text):
        self.writer(text)

    def flush(self):
        pass


class DemoFileHandler(Handler):

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    # Runner for executing code when the run button is pressed.
    runner = Instance(CodeRunnerBase)

    #: Run the demo file
    run_button = Button(image=ImageResource("run"), label="Run")

    #: The current 'info' object (for use by the 'write' method):
    info = Instance(UIInfo)

    def _run_button_changed(self):
        """ Run button is pressed. Rerun the code.
        """
        self.runner.stop()

        demo_file = self.info.object

        def write_to_log(text):
            demo_file.log += text

        self.runner.start(
            code=demo_file.source,
            script_name=demo_file.path,
            init_globals=demo_file.parent.init_dic,
            stdout=_StreamMock(write_to_log),
            stderr=_StreamMock(write_to_log),
        )
        self.info.object.locals = self.runner.locals

    def init(self, info):
        # Save the reference to the current 'info' object:
        self.info = info
        demo_file = info.object
        demo_file.init()

    def closed(self, info, is_ok):
        """ Closes the view.
        """
        self.runner.stop()
        info.object.finish()


# Create a singleton instance:
demo_file_handler = DemoFileHandler(
    #runner=SubprocessCodeRunner(),
    runner=LocalCodeRunner(),
)


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
        """ Returns whether chidren of this object are allowed or not.
        """
        return self.allows_children

    # -------------------------------------------------------------------------
    #  Returns whether or not the object has children:
    # -------------------------------------------------------------------------

    def tno_has_children(self, node=None):
        """ Returns whether or not the object has children.
        """
        if self._has_children is None:
            self._has_children = self.has_children()

        return self._has_children

    # -------------------------------------------------------------------------
    #  Gets the object's children:
    # -------------------------------------------------------------------------

    def tno_get_children(self, node):
        """ Gets the object's children.
        """
        if self._get_children is None:
            self._get_children = self.get_children()

        return self._get_children

    # -------------------------------------------------------------------------
    #  Returns whether or not the object has children:
    # -------------------------------------------------------------------------

    def has_children(self, node):
        """ Returns whether or not the object has children.
        """
        raise NotImplementedError

    # -------------------------------------------------------------------------
    #  Gets the object's children:
    # -------------------------------------------------------------------------

    def get_children(self):
        """ Gets the object's children.
        """
        raise NotImplementedError


class DemoFileBase(DemoTreeNodeObject):
    #: Parent of this file:
    parent = Any()

    #: Name of file system path to this file:
    path = Property(depends_on='parent.path,name')

    #: Name of the file:
    name = Str()

    #: UI form of the 'name':
    nice_name = Property()

    #: Files don't allow children:
    allows_children = Bool(False)

    #: Description of what the demo does:
    description = HTML()

    #: The base URL for links:
    base_url = Property(depends_on='path')

    #: The css file for this node.
    css_filename = Str("default.css")

    _nice_name = Str()

    def init(self):
        pass

    def finish(self):
        pass

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
        """ Returns whether or not the object has children.
        """
        return False

    def get_children(self):
        """ Gets the demo file's children.
        """
        return []


class DemoFile(DemoFileBase):

    #: Source code for the demo:
    source = Code()

    #: Local namespace for executed code:
    locals = Dict(Str, Any)

    #: Content for STDOUT/STDERR to be displayed:
    log = Str()

    def init(self):
        super().init()
        description, source = parse_source(self.path)
        self.description = publish_html_str(description, self.css_filename)
        self.source = source
        self.log = ""

    def finish(self):
        self.locals = {}

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


class DemoContentFile(DemoFileBase):

    def init(self):
        super().init()
        file_str = _read_file(self.path)
        self.description = publish_html_str(file_str, self.css_filename)


class DemoImageFile(DemoFileBase):

    def init(self):
        super().init()
        rst_content = ".. image:: {}".format(self.name)
        self.description = publish_html_str(rst_content, self.css_filename)


class DemoPath(DemoTreeNodeObject):
    """ This class represents a directory.
    """

    # -------------------------------------------------------------------------
    #  Trait definitions:
    # -------------------------------------------------------------------------

    #: Parent of this package:
    parent = Any()

    #: Name of file system path to this package:
    path = Property(depends_on='parent.path,name')

    #: Description of what the demo does:
    description = Property(HTML, depends_on="path,css_filename")

    #: The base URL for links:
    base_url = Property(depends_on='path')

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
            ".txt": DemoContentFile
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
        """ Returns whether or not the object has children.
        """
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
        """ Gets the object's children.
        """
        if self.config_dict or self.config_filename:
            children = self.get_children_from_config()
        else:
            children = self.get_children_from_datastructure()
        return children

    # -------------------------------------------------------------------------
    #  Gets the object's children based on the filesystem structure.
    # -------------------------------------------------------------------------
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
                    dirs.append(
                        DemoPath(
                            parent=self,
                            name=name,
                            css_filename=join('..', self.css_filename)
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
                            "..", self.css_filename)
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
        """ Process a file based on its extension.
        """
        _, ext = splitext(filename)
        file_factory = self._file_factory[ext]
        demo_file = file_factory(parent=self, name=filename)
        return demo_file


class DemoVirtualDirectory(DemoTreeNodeObject):
    """ A class to represent a virtual directory that can contain
    many other demo resources as nested objects, without actually requiring
    the resources to be hosted in a common directory.
    """

    #: Description for this virtual directory.
    description = Str()

    # List of objects to be used as children nodes.
    resources = List(Instance(DemoTreeNodeObject))

    # This node can have children. This changes the icon on the view.
    allows_children = Bool(True)

    # This is the label shown on the view.
    nice_name = Str("Data")

    def has_children(self):
        return len(self.resources) > 0

    def get_children(self):
        return self.resources


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
                open_externally=True,
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
            VGroup(
                Tabbed(
                    Item(
                        "log",
                        style="readonly",
                        editor=CodeEditor(
                            show_line_numbers=False,
                            selected_color=0xFFFFFF
                        ),
                        label="Output",
                        show_label=False
                    ),
                    Item(
                        "locals",
                        editor=ShellEditor(share=True),
                        label="Shell",
                        show_label=False
                    ),
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

demo_virtual_dir_view = View(
    UItem(
        "description",
        style="readonly",
    ),
    id="demo_virtual_dir_view",
    kind="subpanel",
)


demo_tree_editor = TreeEditor(
    nodes=[
        ObjectTreeNode(
            node_for=[DemoPath],
            label="nice_name",
            view=demo_path_view,
        ),
        ObjectTreeNode(
            node_for=[DemoFile],
            label="nice_name",
            view=demo_file_view
        ),
        ObjectTreeNode(
            node_for=[DemoContentFile],
            label="nice_name",
            view=demo_content_view
        ),
        ObjectTreeNode(
            node_for=[DemoImageFile],
            label="nice_name",
            view=demo_content_view
        ),
        ObjectTreeNode(
            node_for=[DemoVirtualDirectory],
            label="nice_name",
            view=demo_virtual_dir_view,
        ),
    ],
    hide_root=True,
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
    model = Instance(DemoTreeNodeObject)

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
        if self.model.has_children():
            self.selected_node = self.model.get_children()[0]

    def _get__next_node(self):
        if self.selected_node is None:
            return None
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
        if self.selected_node is None:
            return None
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
            icon=ImageResource("enthought-icon"),
        )


# -------------------------------------------------------------------------
#  Utilities to convert rst strings/files to html.
# -------------------------------------------------------------------------


def _get_settings(css_path=None):
    """ Helper function to make settings dictionary
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
    """ Format RST string to html using `docutils` if available.
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
    return publish_string(rst_str,
                          writer_name='html',
                          settings_overrides=settings)


def publish_html_file(rst_file_path, html_out_path, css_path=None):
    """ Format reStructuredText in `rst_file_path` to html using `docutils`
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
    publish_file(source_path=rst_file_path,
                 destination_path=html_out_path,
                 writer_name='html',
                 settings_overrides=settings)


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
