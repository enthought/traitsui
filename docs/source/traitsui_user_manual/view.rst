.. _the-view-and-its-building-blocks:

================================
The View and Its Building Blocks
================================

A simple way to edit (or simply observe) the attribute values of a
:term:`HasTraits` object in a GUI window is to call the object's
configure_traits() [3]_ method. This method constructs and displays a window
containing editable fields for each of the object's :term:`trait attribute`\ s.
For example, the following sample code [4]_ defines the SimpleEmployee class,
creates an object of that class, and constructs and displays a GUI for the
object:

.. index::
   pair: examples; configure_traits()

.. _example-1-using-configure-traits:

.. rubric:: Example 1: Using configure_traits()

::

    # configure_traits.py -- Sample code to demonstrate configure_traits()
    from traits.api import HasTraits, Int, Str


    class SimpleEmployee(HasTraits):
        first_name = Str()
        last_name = Str()
        department = Str()

        employee_number = Str()
        salary = Int()


    sam = SimpleEmployee()
    sam.configure_traits()

Unfortunately, the resulting form simply displays the attributes of the object
**sam** in alphabetical order with little formatting, which is seldom what is
wanted:

.. figure:: images/ui_for_ex1.jpg
   :alt: Dialog box showing all attributes of SimpleEmployee in alphabetical order

   Figure 1: User interface for Example 1

.. index::
   object: View

.. _the-view-object:

The View Object
---------------

In order to control the layout of the interface, it is necessary to define a
View object. A View object is a template for a GUI window or panel. In other
words, a View specifies the content and appearance of a TraitsUI window or
panel display.

For example, suppose you want to construct a GUI window that shows only the
first three attributes of a SimpleEmployee (e.g., because salary is confidential
and the employee number should not be edited). Furthermore, you would like to
specify the order in which those fields appear. You can do this by defining a
View object and passing it to the configure_traits() method:

.. index:: configure_traits(); view parameter, examples; View object


.. _example-2-using-configure-traits-with-a-view-object:

.. rubric:: Example 2: Using configure_traits() with a View object

.. literalinclude:: examples/configure_traits_view.py
   :start-at: configure_traits_view.py

The resulting window has the desired appearance:

.. figure:: images/ui_for_ex2.jpg
   :alt: User interface showing only First name, Last name, and Department

   Figure 2: User interface for Example 2

A View object can have a variety of attributes, which are set in the View
definition, following any Group or Item objects.

The sections on :ref:`contents-of-a-view` through :ref:`advanced-view-concepts`
explore the contents and capabilities of Views. Refer to
the *Traits API Reference* for details of the View class.

Except as noted, all example code uses the configure_traits() method; a detailed
description of this and other techniques for creating GUI displays from Views
can be found in :ref:`displaying-a-view`.

.. index:: View; contents
   object: View

.. _contents-of-a-view:

Contents of a View
------------------

The contents of a View are specified primarily in terms of two basic building
blocks: Item objects (which, as suggested by Example 2, correspond roughly to
individual trait attributes), and Group objects. A given View definition can
contain one or more objects of either of these types, which are specified as
arguments to the View constructor, as in the case of the three Items in Example
2.

The remainder of this chapter describes the Item and Group classes.

.. index:: widget, control
   object: Item

.. _the-item-object:

The Item Object
```````````````

The simplest building block of a View is the :term:`Item` object. An Item
specifies a single interface :term:`widget`, usually the display for a single
trait attribute of a HasTraits object. The content, appearance, and behavior of
the widget are controlled by means of the Item object's attributes, which are
usually specified as keyword arguments to the Item constructor, as in the case
of *name* in Example 2.

The remainder of this section describes the attributes of the Item object,
grouped by categories of functionality. It is not necessary to understand all of
these attributes in order to create useful Items; many of them can usually be
left unspecified, as their default values are adequate for most purposes.
Indeed, as demonstrated by earlier examples, simply specifying the name of the
trait attribute to be displayed is often enough to produce a usable result.

The following table lists the attributes of the Item class, organized by
functional categories. Refer to the *Traits API Reference* for details on the
Item class.

.. index:: attributes; Item, Item; attributes
.. index:: name attribute, dock attribute; Item, emphasized attribute
.. index:: export attribute; Item, height attribute; Item, image attribute;
.. index:: Item, label attribute; Item, padding attribute; Item
.. index:: resizable attribute, show_label attribute, springy attribute; Item
.. index:: width attribute; Item, format_str attribute, format_func attribute
.. index:: editor attribute, style attribute; Item, enabled_when attribute; Item
.. index:: visible_when attribute; Item, defined_when attribute; Item
.. index:: has_focus attribute, tooltip attribute, help attribute; Item
.. index:: help_id attribute; Item, id attribute; Item

.. _attributes-of-item-by-category-table:

.. rubric:: Attributes of Item, by category

Content
    These attributes specify the actual data to be displayed by an item.
    Because an Item is essentially a template for displaying a single trait,
    its **name** attribute is nearly always specified.

    name: str
        The name of the trait being edited.

Display format
   In addition to specifying which trait attributes are to be displayed, you
   might need to adjust the format of one or more of the resulting widgets.

   If an Item's **label** attribute is specified but not its name, the value
   of **label** is displayed as a simple, non-editable string. (This feature
   can be useful for displaying comments or instructions in a TraitsUI
   window.)

   dock:
      Docking style for the item.
   emphasized: bool
      Should label text be emphasized?
   export:
      Category of elements dragged from view.
   height:
      Requested height as pixels (height > 1) or proportion of screen (0 <
      height < 1)
   image:
      Image to show on tabs.
   label: str
      The label to display on the item.
   padding: int
      Amount of extra space, in pixels, to add around the item. Values must be
      integers between -15 and 15. Use negative values to subtract from the
      default spacing.
   resizable: bool
      Can the item be resized to use extra space. The default is False.
   show_label: bool
      Whether to show the label or not (defaults to True).
   springy: bool
      Use extra space in the parent layout? The default is False.
   width: float
      Requested width as pixels (width > 1) or proportion of screen (0 < width
      < 1).

Content format
   In some cases it can be desirable to apply special formatting to a widget's
   contents rather than to the widget itself. Examples of such formatting
   might include rounding a floating-point value to two decimal places, or
   capitalizing all letter characters in a license plate number.

   format_str: str
      '% format' string for text.
   format_func: func
      Format function for text.

Widget override
   These attributes override the widget that is automatically
   selected by TraitsUI. These options are discussed in
   :ref:`introduction-to-trait-editor-factories` and
   :ref:`the-predefined-trait-editor-factories`.

   editor: ItemEditor
      Editor to use.
   style: {'simple', 'custom', 'text', 'readonly'}
      The editor style (see :ref:`specifying-an-editor-style`).

Visibility and status
   Use these attributes to create a simple form of a dynamic GUI, which
   alters the display in response to changes in the data it contains.
   More sophisticated dynamic behavior can be implemented using a custom
   :term:`Handler` (see :ref:`controlling-the-interface-the-handler`).

   enabled_when: str
      Python expression that determines whether the group can be edited.
      The expression will be evaluated any time a trait on an object in the
      UI's context is changed. As a result, changes to nested traits that don't
      also change a trait on some object in the context may not trigger the
      expression to be evaluated.
   visible_when: str
      Python expression that determines visibility of group. The expression
      will be evaluated any time a trait on an object in the UI's context is
      changed. As a result, changes to nested traits that don't also change a
      trait on some object in the context may not trigger the expression to be
      evaluated.
   defined_when: str
      Expression that determines inclusion of group in parent.
   has_focus: bool
      Should this item get initial focus?

User help
   These attributes provide guidance to the user in using the user interface.

   tooltip: str
      Tooltip to display on mouse-over.
   help:
      If the **help** attribute is not defined for an Item, a system-generated
      message is used instead.
   help_id:
      It is ignored by the default help handler, but can be used by a custom
      help handler.

   .. TODO: Add sample help screen

Unique identifier
   id:
      Used as a key for saving user preferences about the widget. If **id** is
      not specified, the value of the **name** attribute is used.

.. index:: Custom class, Label class, Heading class, Readonly class,
   Spring class, UCustom class, UItem class, UReadonly class
   pair: Item; subclasses

.. _subclasses-of-item:

Subclasses of Item
``````````````````

The TraitsUI package defines the following subclasses of Item, which are helpful
shorthands for defining certain types of items. Label, Heading and Spring are
intended to help with the layout of a TraitsUI View, and need not have a trait
attribute associated with them. For example, ``Spring()`` and
``Label("This is a label")`` are valid code.

+-----------+------------------------------+-----------------------------------------+
| Subclass  | Description                  | Equivalent To                           |
+===========+==============================+=========================================+
| Label     | An item that is just a label |                                         |
|           | and doesn't require a trait  |                                         |
|           | name associated with it      |                                         |
+-----------+------------------------------+-----------------------------------------+
| Heading   | A fancy label                |                                         |
+-----------+------------------------------+-----------------------------------------+
| Spring    | A item that expands to  take | :samp:`Item(name='spring',              |
|           | as much space as necessary   | springy=True, show_label=False)`        |
+-----------+------------------------------+-----------------------------------------+
| Custom    | An item with a custom editor | :samp:`Item(style='custom')`            |
|           | style                        |                                         |
+-----------+------------------------------+-----------------------------------------+
| Readonly  | An item with a readonly      | :samp:`Item(style='readonly')`          |
|           | editor style                 |                                         |
+-----------+------------------------------+-----------------------------------------+
| UItem     | An item with no label        | :samp:`Item(show_label=False)`          |
+-----------+------------------------------+-----------------------------------------+
| UCustom   | A Custom item with no label  | :samp:`Item(style='custom',             |
|           |                              | show_label=False)`                      |
+-----------+------------------------------+-----------------------------------------+
| UReadonly | A Readonly item  with no     | :samp:`Item(style='readonly',           |
|           | label                        | show_label=False)`                      |
+-----------+------------------------------+-----------------------------------------+

.. index:
   object: Group

.. _the-group-object:

The Group Object
````````````````

The preceding sections have shown how to construct windows that display a simple
vertical sequence of widgets using instances of the View and Item classes. For
more sophisticated interfaces, though, it is often desirable to treat a group of
data elements as a unit for reasons that might be visual (e.g., placing the
widgets within a labeled border) or logical (activating or deactivating the
widgets in response to a single condition, defining group-level help text). In
TraitsUI, such grouping is accomplished by means of the :term:`Group` object.

Consider the following enhancement to Example 2:

.. index::
   pair: configure_traits(); examples
   triple: View; Group; examples

.. _example-3-using-configure-traits-with-a-view-and-a-group-object:

.. rubric:: Example 3: Using configure_traits() with a View and a Group object

.. literalinclude:: examples/configure_traits_view_group.py
   :start-at: configure_traits_view_group.py

The resulting window shows the same widgets as before, but they are now enclosed
in a visible border with a text label:

.. figure:: images/ui_for_ex3.jpg
   :alt: User interface showing three fields enclosed in a border

   Figure 3: User interface for Example 3

.. indexx:
   pair: contents; Group

.. _content-of-a-group:

Content of a Group
::::::::::::::::::

The content of a Group object is specified exactly like that of a View object.
In other words, one or more Item or Group objects are given as arguments to the
Group constructor, e.g., the three Items in Example 3. [5]_ The objects
contained in a Group are called the *elements* of that Group. Groups can be
nested to any level.

.. index::
   pair: attributes; Group

.. _group-attributes:

Group Attributes
::::::::::::::::

The following table lists the attributes of the Group class, organized by
functional categories. As with Item attributes, many of these attributes can
be left unspecified for any given Group, as the default values usually lead to
acceptable displays and behavior.

See the *Traits API Reference* for details of the Group class.

.. index:: object attribute; Group, content attribute; Group
.. index:: label attribute; Group, show_border attribute, show_labels attribute
.. index:: show_left attribute, padding attribute; Group, layout attribute
.. index:: selected attribute, orientation attribute, style attribute; Group
.. index:: columns attribute, dock attribute; Group, dock_theme attribute;
.. index:: Group, image attribute; Group export attribute; Group,
.. index:: springy attribute; Group


.. _attributes-of-group-by-category-table:

.. rubric:: Attributes of Group, by category

Content
   object:
      References the object whose traits are being edited by members of the
      group; by default this is 'object', but could be another object in the
      current context.
   content: list
      List of elements in the group.

Display format
   These attributes define display options for the group as a whole.

   columns:
      The number of columns in the group.
   dock:
      Dock style of sub-groups.
   dock_theme:
      The theme to use for the dock.
   export:
      Category of elements dragged from view.
   image:
      Image to show on tabs.
   label:
      The label to display on the group.
   layout: {'normal', 'flow', 'split', 'tabbed'}
      Layout style of the group, which can be one of the following:

      * 'normal' (default): Sub-groups are displayed sequentially in a single
        panel.
      * 'flow': Sub-groups are displayed sequentially, and then "wrap" when
        they exceed the available space in the **orientation** direction.
      * 'split': Sub-groups are displayed in a single panel, separated by
        "splitter bars", which the user can drag to adjust the amount of space
        for each sub-group.
      * 'tabbed': Each sub-group appears on a separate tab, labeled with the
        sub-group's *label* text, if any.

      This attribute is ignored for groups that contain only items, or contain
      only one sub-group.
   orientation: {'vertical', 'horizontal'}
      The orientation of the subgroups.
   padding: int
      Amount of extra space, in pixels, to add around the item. Values must be
      integers between -15 and 15. Use negative values to subtract from the
      default spacing.
   selected:
      In a tabbed layout, should this be the visible tab?
   show_border: bool
      Should a border be shown or not
   show_labels:
      Show the labels of items?
   show_left: bool
      Show labels on the left or the right.
   springy: bool
      Use extra space in the parent layout? The default is False.
   style: {'simple', 'custom', 'text', 'readonly'}
      Default editor style of items in the group.

   .. index:: enabled_when attribute; Group
   .. index:: visible_when attribute; Group
   .. index:: defined_when attribute; Group
   .. index:: help attribute; Group
   .. index:: help_id attribute; Group
   .. index:: id attribute; Group

Visibility and status
   These attributes work similarly to the attributes of the same names on the Item class.

   enabled_when: str
      Python expression that determines whether the group can be edited.
      The expression will be evaluated any time a trait on an object in the
      UI's context is changed. As a result, changes to nested traits that don't
      also change a trait on some object in the context may not trigger the
      expression to be evaluated.
   visible_when: str
      Python expression that determines visibility of group. The expression
      will be evaluated any time a trait on an object in the UI's context is
      changed. As a result, changes to nested traits that don't also change a
      trait on some object in the context may not trigger the expression to be
      evaluated.
   defined_when: str
      Expression that determines inclusion of group in parent.

   .. TODO: Does Item-level or Group-level take precedence? Find out and document.

User help
   The help text is used by the default help handler only if the group is the
   only top-level group for the current View. For example, suppose help text
   is defined for a Group called **group1**. The following View shows this
   text in its help window::

     View(group1)

   The following two do not::

     View(group1, group2)
     View(Group(group1))

   help: str
      Help message. If the **help** attribute is not defined, a
      system-generated message is used instead.
   help_id:
      The **help_id** attribute is ignored by the default help handler, but can be
      used by a custom help handler.

   .. TODO: The document needs to include material on organizing Views via
      Groups, including the implied top-level group of every View. If we do
      thiss earlier in the document, it will probably simplify this.

Unique identifier
   id: str
      The **id** attribute is used as a key for saving user preferences about
      the widget. If **id** is not specified, the **id** values of the elements
      of the group are concatenated and used as the group identifier.


.. index::
   pair: subclasses; Group

.. _subclasses-of-group:

Subclasses of Group
```````````````````

The TraitsUI package defines the following subclasses of Group, which are
helpful shorthands for defining certain types of groups. Refer to the *Traits
API Reference* for details.

.. index:: HGroup, HFlow, HSplit, Tabbed, VGroup, VFlow, VGrid, VFold, VSplit

.. _subclasses-of-group_table:

.. rubric:: Subclasses of Group

+-----------+------------------------------+-----------------------------------------+
|Subclass   |Description                   |Equivalent To                            |
+===========+==============================+=========================================+
|HGroup     |A group whose items are laid  |:samp:`Group(orientation='horizontal')`  |
|           |out horizontally.             |                                         |
+-----------+------------------------------+-----------------------------------------+
|HFlow      |A horizontal group whose items|:samp:`Group(orientation='horizontal',   |
|           |"wrap" when they exceed the   |layout='flow', show_labels=False)`       |
|           |available horizontal space.   |                                         |
+-----------+------------------------------+-----------------------------------------+
|HSplit     |A horizontal group with       |:samp:`Group(orientation='horizontal',   |
|           |splitter bars to separate it  |layout='split')`                         |
|           |from other groups.            |                                         |
+-----------+------------------------------+-----------------------------------------+
|Tabbed     |A group that is shown as a tab|:samp:`Group(orientation='horizontal'    |
|           |in a notebook.                |layout='tabbed', springy=True)`          |
+-----------+------------------------------+-----------------------------------------+
|VGroup     |A group whose items are laid  |:samp:`Group(orientation='vertical')`    |
|           |out vertically.               |                                         |
+-----------+------------------------------+-----------------------------------------+
|VFlow      |A vertical group whose items  |:samp:`Group(orientation='vertical',     |
|           |"wrap" when they exceed the   |layout='flow', show_labels=False)`       |
|           |available vertical space.     |                                         |
+-----------+------------------------------+-----------------------------------------+
|VFold      |A vertical group in which     |:samp:`Group(orientation='vertical',     |
|           |items can be collapsed (i.e., |layout='fold', show_labels=False)`       |
|           |folded) by clicking their     |                                         |
|           |titles.                       |                                         |
+-----------+------------------------------+-----------------------------------------+
|VGrid      |A vertical group whose items  |:samp:`Group(orientation='vertical',     |
|           |are laid out in two columns.  |columns=2)`                              |
+-----------+------------------------------+-----------------------------------------+
|VSplit     |A vertical group with splitter|:samp:`Group(orientation='vertical',     |
|           |bars to separate it from other|layout='split')`                         |
|           |groups.                       |                                         |
+-----------+------------------------------+-----------------------------------------+


.. rubric:: Footnotes

.. [3] If the code is being run from a program that already has a GUI defined,
   then use edit_traits() instead of configure_traits(). These methods are
   discussed in more detail in :ref:`displaying-a-view`.

.. [4] All code examples in this guide that include a file name are also
   available as examples in the :file:`tutorials/doc_examples/examples`
   subdirectory of the Traits docs directory. You can run them individually,
   or view them in a tutorial program by running:
   :program:`python` :file:`{Traits_dir}/tutorials/tutor.py` :file:`{Traits_dir}/docs/tutorials/doc_examples`

.. [5] As with Views, it is possible for a Group to contain objects of more than
   one type, but it is not recommended.
