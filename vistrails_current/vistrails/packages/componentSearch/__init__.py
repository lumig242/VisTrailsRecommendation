from component_search_form import ComponentSearchForm
from networkx_graph import TestForm

identifier = 'edu.cmu.sv.componentSearch'
name = 'Recommendation'
version = '1.0.0'

component_search_form = ComponentSearchForm()


def menu_items():
    """menu_items() -> tuple of (str,function)
    It returns a list of pairs containing text for the menu and a
    callback function that will be executed when that menu item is selected.
    """
    def show_search_form():

        component_search_form.show_main_window()

    lst = []
    lst.append(("Start Recommendation Engine", show_search_form))
    print 'Test menu items'
    return tuple(lst)
