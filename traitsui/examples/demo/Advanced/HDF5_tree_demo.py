# (C) Copyright 2004-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

"""This demo shows how to use Traits TreeEditors with PyTables to walk the
hierarchy of an HDF5 file.  This only picks out tables, arrays and groups, but could
easily be extended to other structures.

In the demo, the path to the selected item is printed whenever the selection
changes. An example HDF5 file is provided here, but you could easily change
the path given at the bottom of this file to a path to your own HDF5 file.

To run this demonstration successfully, you must have the following packages
installed:

- **PyTables** (``tables``)
- **HDF5 for Python** (``h5py``)

Note that PyTables can't read HDF5 files created with h5py,
but h5py can read HDF5 files created with PyTables. See HDF5_tree_demo2 for
an example using h5py.
"""
import os
import tables as tb

from traits.api import HasTraits, Str, List, Instance, Any
from traitsui.api import TreeEditor, TreeNode, View, Item, Group

ROOT = os.path.dirname(__file__)

# View for objects that aren't edited
no_view = View()


# HDF5 Nodes in the tree
class Hdf5ArrayNode(HasTraits):
    name = Str('<unknown>')
    path = Str('<unknown>')
    parent_path = Str('<unknown>')


class Hdf5GroupNode(HasTraits):
    name = Str('<unknown>')
    path = Str('<unknown>')
    parent_path = Str('<unknown>')
    # Can't have recursive traits?  Really?
    # groups = List(Hdf5GroupNode)
    groups = List()
    arrays = List(Hdf5ArrayNode)
    groups_and_arrays = List()


class Hdf5FileNode(HasTraits):
    name = Str('<unknown>')
    path = Str('/')
    groups = List(Hdf5GroupNode)
    arrays = List(Hdf5ArrayNode)
    groups_and_arrays = List()


# Recursively build tree, there is probably a better way of doing this.


def _get_sub_arrays(group, h5file):
    """Return a list of all arrays immediately below a group in an HDF5 file."""
    return [
        Hdf5ArrayNode(
            name=array._v_name,
            path=array._v_pathname,
            parent_path=array._v_parent._v_pathname,
        )
        for array in group
        if isinstance(array, (tb.Array, tb.Table))
    ]  # More pythonic
    # for array in h5file.iter_nodes(group, classname='Array')]  # Old call


def _get_sub_groups(group, h5file):
    """Return a list of all groups and arrays immediately below a group in an HDF5 file."""
    subgroups = []

    for subgroup in h5file.iter_nodes(group, classname='Group'):
        subsubgroups = _get_sub_groups(subgroup, h5file)
        subsubarrays = _get_sub_arrays(subgroup, h5file)
        subgroups.append(
            Hdf5GroupNode(
                name=subgroup._v_name,
                path=subgroup._v_pathname,
                parent_path=subgroup._v_parent._v_pathname,
                groups=subsubgroups,
                arrays=subsubarrays,
                groups_and_arrays=subsubgroups + subsubarrays,
            )
        )
    return subgroups


def _hdf5_tree(filename):
    """Return a list of all groups and arrays below the root group of an HDF5 file."""

    with tb.open_file(filename, 'r') as h5file:
        subgroups = _get_sub_groups(h5file.root, h5file)
        subarrays = _get_sub_arrays(h5file.root, h5file)
    h5_tree = Hdf5FileNode(
        name=filename,
        groups=subgroups,
        arrays=subarrays,
        groups_and_arrays=subgroups + subarrays,
    )

    return h5_tree


# Get a tree editor


def _hdf5_tree_editor(selected=''):
    """Return a TreeEditor specifically for HDF5 file trees."""
    return TreeEditor(
        nodes=[
            TreeNode(
                node_for=[Hdf5FileNode],
                auto_open=True,
                children='groups_and_arrays',
                label='name',
                view=no_view,
            ),
            TreeNode(
                node_for=[Hdf5GroupNode],
                auto_open=False,
                children='groups_and_arrays',
                label='name',
                view=no_view,
            ),
            TreeNode(
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


class ATree(HasTraits):
    h5_tree = Instance(Hdf5FileNode)
    node = Any()

    traits_view = View(
        Group(
            Item(
                'h5_tree',
                editor=_hdf5_tree_editor(selected='node'),
                resizable=True,
                show_label=False,
            ),
            orientation='vertical',
        ),
        title='HDF5 Tree Example',
        buttons=['Undo', 'OK', 'Cancel'],
        resizable=True,
        width=0.3,
        height=0.3,
    )

    def _node_changed(self):
        print(self.node.path)


def make_test_datasets():
    """Makes the test datasets and store it in the current folder"""
    import h5py
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
    import sys

    filename = os.path.join(ROOT, 'test_fixed.h5')
    filename = os.path.join(ROOT, 'test_table_no_dc.h5')
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    a_tree = ATree(h5_tree=_hdf5_tree(filename))
    return a_tree


demo = main()


if __name__ == '__main__':
    # make_test_datasets()
    demo.configure_traits()
