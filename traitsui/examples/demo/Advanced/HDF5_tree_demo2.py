# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""This demo shows how to use Traits TreeEditors with h5py to walk the
hierarchy of several HDF5 files in a folder.  All Datasets and Groups are shown for each file.

In the demo, the path to the selected item is printed whenever the selection
changes. An example HDF5 file is provided here, but you could easily change
the path given at the bottom of this file to a path to your own HDF5 file.

To run this demonstration successfully, you must have the following packages
installed:

- **PyTables** (``tables``)
- **HDF5 for Python** (``h5py``)

Note that PyTables can't read HDF5 files created with h5py,
but h5py can read HDF5 files created with PyTables. See HDF5_tree_demo for
an example using PyTables.
"""

import os
import warnings
import h5py

from traits import api
import traitsui.api as ui


ROOT = os.path.dirname(__file__)


# View for objects that aren't edited
no_view = ui.View()


# HDF5 Nodes in the tree
class Hdf5ArrayNode(api.HasTraits):
    name = api.Str('<unknown>')
    path = api.Str('<unknown>')
    parent_path = api.Str('<unknown>')


class Hdf5GroupNode(api.HasTraits):
    name = api.Str('<unknown>')
    path = api.Str('<unknown>')
    parent_path = api.Str('<unknown>')
    # Can't have recursive traits?  Really?
    # groups = api.List( Hdf5GroupNode )
    groups = api.List()
    arrays = api.List(Hdf5ArrayNode)
    groups_and_arrays = api.List()


class Hdf5FileNode(api.HasTraits):
    name = api.Str('<unknown>')
    path = api.Str('/')
    groups = api.List(Hdf5GroupNode)
    arrays = api.List(Hdf5ArrayNode)
    groups_and_arrays = api.List()


class Hdf5FilesNode(api.HasTraits):
    name = api.Str('<unknown>')
    path = api.Str('/')
    files = api.List(Hdf5FileNode)
    groups_and_arrays = api.List()


# Recursively build tree, there is probably a better way of doing this.


def _get_sub_arrays(group, parent_path):
    """Return a list of all arrays immediately below a group in an HDF5 file."""
    return [
        Hdf5ArrayNode(
            name=name, path=parent_path + name, parent_path=parent_path
        )
        for name, array in group.items()
        if isinstance(array, h5py.Dataset)
    ]


def _get_sub_groups(group, parent_path):
    """Return a list of all subgroups and arrays immediately below a group in an HDF5 file."""
    subgroups = []

    for name, subgroup in group.items():
        if isinstance(subgroup, h5py.Group):
            path = parent_path + name + '/'
            subsubarrays = _get_sub_arrays(subgroup, path)
            subsubgroups = _get_sub_groups(subgroup, path)
            subgroups.append(
                Hdf5GroupNode(
                    name=name,
                    path=path,
                    parent_path=parent_path,
                    arrays=subsubarrays,
                    subgroups=subsubgroups,
                    groups_and_arrays=subsubgroups + subsubarrays,
                )
            )

    return subgroups


def _hdf5_tree(filename):
    with h5py.File(filename, 'r') as h5file:
        path = (
            filename + '#'
        )  # separate dataset name from name of hdf5-filename
        subgroups = _get_sub_groups(h5file, path)
        subarrays = _get_sub_arrays(h5file, path)
    file_tree = Hdf5FileNode(
        name=os.path.basename(filename),
        path=filename,
        groups=subgroups,
        arrays=subarrays,
        groups_and_arrays=subgroups + subarrays,
    )

    return file_tree


def _hdf5_trees(filenames):
    """Return a list of all groups and arrays below the root group of an HDF5 file."""
    if isinstance(filenames, str):
        filenames = [filenames]
    files_tree = Hdf5FilesNode()
    files_tree.name = root = os.path.dirname(filenames[0])
    files_tree.path = root

    for filename in filenames:
        folder = os.path.dirname(filename)
        if folder != root:
            warnings.warn(
                "Expected same folder for all files, but got {} != {}".format(
                    root, folder
                )
            )
        file_tree = _hdf5_tree(filename)

        files_tree.files.append(file_tree)
        files_tree.groups_and_arrays.extend(file_tree.groups_and_arrays)
    return files_tree


# Get a tree editor


def _hdf5_tree_editor(selected=''):
    """Return a ui.TreeEditor specifically for HDF5 file trees."""
    return ui.TreeEditor(
        nodes=[
            ui.TreeNode(
                node_for=[Hdf5FilesNode],
                auto_open=True,
                children='files',
                label='name',
                view=no_view,
            ),
            ui.TreeNode(
                node_for=[Hdf5FileNode],
                auto_open=True,
                children='groups_and_arrays',
                label='name',
                view=no_view,
            ),
            ui.TreeNode(
                node_for=[Hdf5GroupNode],
                auto_open=False,
                children='groups_and_arrays',
                label='name',
                view=no_view,
            ),
            ui.TreeNode(
                node_for=[Hdf5ArrayNode],
                auto_open=False,
                children='',
                label='name',
                view=no_view,
            ),
        ],
        editable=False,
        selected=selected,
    )


class _H5Tree(api.HasTraits):
    h5_tree = api.Instance(Hdf5FileNode)
    node = api.Any()
    path = api.Str()

    traits_view = ui.View(
        ui.Group(
            ui.Item(
                'h5_tree',
                editor=_hdf5_tree_editor(selected='node'),
                resizable=True,
            ),
            ui.Item('path', label='Selected node'),
            orientation='vertical',
        ),
        title='HDF5 Tree Example',
        buttons=['OK', 'Cancel'],
        resizable=True,
        width=0.3,
        height=0.3,
    )

    def _node_changed(self):
        self.path = self.node.path
        print(self.node.path)


class _H5Trees(api.HasTraits):
    h5_trees = api.Instance(Hdf5FilesNode)
    node = api.Any()
    path = api.Str()

    traits_view = ui.View(
        ui.Group(
            ui.Item(
                'h5_trees',
                editor=_hdf5_tree_editor(selected='node'),
                resizable=True,
            ),
            ui.Item('path', label='Selected node'),
            orientation='vertical',
        ),
        title='Multiple HDF5 file Tree Example',
        buttons=['OK', 'Cancel'],
        resizable=True,
        width=0.3,
        height=0.3,
    )

    def _node_changed(self):
        self.path = self.node.path
        print(self.node.path)


def hdf5_tree(filename):
    # if isinstance(filename, str):
    #     return _H5Tree(h5_tree=_hdf5_tree(filename))
    return _H5Trees(h5_trees=_hdf5_trees(filename))


def make_test_datasets():
    """Makes the test datasets and store it in the current folder"""
    import numpy as np
    import pandas as pd  # pandas uses pytables to store datasets in hdf5 format.
    from random import randrange

    n = 100

    df = pd.DataFrame(
        dict(
            [
                ("int{0}".format(i), np.random.randint(0, 10, size=n))
                for i in range(5)
            ]
        )
    )

    df['float'] = np.random.randn(n)

    for i in range(10):
        df["object_1_{0}".format(i)] = [
            '%08x' % randrange(16 ** 8) for _ in range(n)
        ]

    for i in range(7):
        df["object_2_{0}".format(i)] = [
            '%15x' % randrange(16 ** 15) for _ in range(n)
        ]

    df.info()
    df.to_hdf('test_fixed.h5', 'data', format='fixed')
    df.to_hdf('test_table_no_dc.h5', 'data', format='table')
    df.to_hdf('test_table_dc.h5', 'data', format='table', data_columns=True)
    df.to_hdf(
        'test_fixed_compressed.h5',
        'data',
        format='fixed',
        complib='blosc',
        complevel=9,
    )

    # h5py dataset
    time = np.arange(n)
    x = np.linspace(-7, 7, n)
    axes_latlon = [
        ('time', time),
        ('coordinate', np.array(['lat', 'lon'], dtype='S3')),
    ]
    axes_mag = [
        ('time', time),
        ('direction', np.array(['x', 'y', 'z'], dtype='S1')),
    ]
    latlon = np.vstack(
        (np.linspace(-0.0001, 0.00001, n) + 23.8, np.zeros(n) - 82.3)
    ).T
    mag_data = np.vstack(
        (
            -(1 - np.tanh(x) ** 2) * np.sin(2 * x),
            -(1 - np.tanh(x) ** 2) * np.sin(2 * x),
            -(1 - np.tanh(x) ** 2),
        )
    ).T
    datasets = (
        axes_mag
        + axes_latlon
        + [('magnetic_3_axial', mag_data), ('latlon', latlon)]
    )
    with h5py.File(os.path.join(ROOT, 'test_h5pydata.h5'), "a") as h5file:
        h5group = h5file.require_group("run1_test1")
        for data_name, data in datasets:
            h5group.require_dataset(
                name=data_name,
                dtype=data.dtype,
                shape=data.shape,
                data=data,
                # **options
            )


def main():
    filenames = [
        'test_fixed.h5',
        'test_table_no_dc.h5',
        'test_table_dc.h5',
        'test_fixed_compressed.h5',
        'test_h5pydata.h5',
    ]
    fullfiles = [os.path.join(ROOT, fname) for fname in filenames]
    h5_trees = hdf5_tree(fullfiles)
    return h5_trees


demo = main()


if __name__ == '__main__':
    # make_test_datasets()
    ok_status = demo.configure_traits()
    print('The End', ok_status)
