from traits.api import HasTraits, List, Float, Instance
from traitsui.api import View, Item, CSVListEditor, ModelView

from _tools import *


class ListOfFloats(HasTraits):
    data = List(Float)


class ListOfFloatsWithCSVEditor(ModelView):
    model = Instance(ListOfFloats)

    traits_view = View(
        Item(label="Close the window to append data"),
        Item('model.data', editor = CSVListEditor()),
        buttons = ['OK']
    )


def test_csv_editor_disposal():
    # Bug: CSVListEditor does not un-hook the traits notifications after its
    # disposal, causing errors when the hooked data is accessed after
    # the window is closed

    try:
        with store_exceptions_on_all_threads():
            list_of_floats = ListOfFloats(data=[1,2,3])
            csv_view = ListOfFloatsWithCSVEditor(model=list_of_floats)
            ui = csv_view.edit_traits()
            press_ok_button(ui)

            # raise an exception if still hooked
            list_of_floats.data.append(2)

    except AttributeError:
        # if all went well, we should not be here
        assert False, "AttributeError raised"


if __name__ == '__main__':
    # Executing the file opens the dialog for manual testing
    list_of_floats = ListOfFloats(data=[1,2,3])
    csv_view = ListOfFloatsWithCSVEditor(model=list_of_floats)
    csv_view.configure_traits()

    # this call will raise an AttributeError in commit
    # 4ecb2fa8f0ef385d55a2a4062d821b0415777973
    # This is because the editor does not un-hook the traits notifications
    # after its disposal
    list_of_floats.data.append(2)
    print list_of_floats.data
