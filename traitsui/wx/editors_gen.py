#------------------------------------------------------------------------------
# Copyright (c) 2008, Enthought, Inc.
# All rights reserved.
#
# This software is provided without warranty under the terms of the GPL v2
# license.
#
# Author: Vibha Srinivasan <vibha@enthought.com>
#------------------------------------------------------------------------------

""" Generates a file containing definitions for all of the editors defined in
the WX backend.
"""

import os, glob, sys
from traitsui.api import Editor
from traitsui.editor_factory import EditorFactory

def gen_editor_definitions(target_filename):
    """ Generates a file containing definitions for all of the editors
    defined in the Qt backend.
    """

    target_file = open(target_filename, 'w')
    dirpath = os.path.dirname(os.path.abspath(__file__))
    # Find all the files which define a TraitsUIEditor
    editor_files = []
    for (root, dirs, files) in os.walk(dirpath):
        if '.svn' in dirs:
            dirs.remove('.svn')
        editor_files.extend(glob.glob(os.path.join(root, '*_editor.py')))

    for absfilename in editor_files:
        (dirname, filename) = (os.path.dirname(absfilename),
                               os.path.basename(absfilename).rstrip('.py'))
        import_path = 'traitsui.wx' + \
                       dirname.replace(dirpath, '').replace(os.sep, '.') +\
                       '.' + filename
        __import__(import_path)
        module = sys.modules[import_path]
        class_names = []
        for name in dir(module):
            try:
                if issubclass(getattr(module, name), EditorFactory) and \
                    name not in ['EditorFactory', 'BasicEditorFactory']:
                    class_names.append(name)
                elif issubclass(getattr(module, name), Editor) and \
                     name != 'Editor':
                    class_names.append(name)
            except:
                try:
                    if isinstance(getattr(module, name), EditorFactory) or \
                        isinstance(getattr(module, name), Editor):
                        class_names.insert(0, name)
                except:
                    pass

        if len(class_names) > 0:
            # FIXME: Is there a better way to sort these names?
            if 'ToolkitEditorFactory' in class_names:
                class_name = 'ToolkitEditorFactory'
            else:
                class_name = ''.join([name.capitalize() for name in
                                     filename.split('_')])
                if class_name not in class_names:
                    class_name = class_names[0]
            function = "def %(filename)s(*args, **traits):"%locals()
            target_file.write(function)
            target_file.write('\n')
            func_code = ' '*4 + "import %(import_path)s as editor"%locals()+'\n'
            func_code+= ' '*4 + "return editor.%(class_name)s(*args, **traits)" \
                    % locals()
            target_file.write(func_code)
            target_file.write('\n\n')

    target_file.close()
