from traits.api import HasTraits, Str

from traitsui.api import TextEditor, View, Item
from traitsui.testing.tester.ui_tester import UITester
from traitsui.testing.tester import command, query

class Foo(HasTraits):

    name = Str()

    nickname = Str()



def get_view(style, auto_set):
    """ Return the default view for the Foo object.

    Parameters
    ----------
    style : str
        e.g. 'simple', or 'custom'
    auto_set : bool
        To be passed directly to the editor factory.
    """
    return View(
        Item("name", editor=TextEditor(auto_set=auto_set), style=style)
    )

foo = Foo()
view1 = get_view(style="simple", auto_set=True)
view2 = get_view(style="custom", auto_set=True)
if __name__ == '__main__':
    tester = UITester(delay=500)
    with tester.create_ui(foo, dict(view=view1)) as ui:
        name_field = tester.find_by_name(ui, "name")
        name_field.perform(command.KeySequence("NEW"))
        display_name = name_field.inspect(query.DisplayedText())
        assert foo.name == "NEW"
        assert display_name == foo.name
        for _ in range(3):
            name_field.perform(command.KeyClick("Backspace"))

    with tester.create_ui(foo, dict(view=view2)) as ui:
        name_field = tester.find_by_name(ui, "name")
        name_field.perform(command.KeySequence("NEWER"))
        display_name = name_field.inspect(query.DisplayedText())
        assert foo.name == "NEWER"
        assert display_name == foo.name
