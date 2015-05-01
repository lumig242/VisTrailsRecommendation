from cmac_form import CMACForm
from networkx_graph import TestForm

identifier = 'edu.cmu.sv.cmac'
name = 'CMAC All Services'
version = '1.0.0'

cmac_form = CMACForm()


def menu_items():
    """menu_items() -> tuple of (str,function)
    It returns a list of pairs containing text for the menu and a
    callback function that will be executed when that menu item is selected.
    """
    def show_search_form():

        cmac_form.show_main_window()

    lst = []
    lst.append(("Ignore this", show_search_form))
    return tuple(lst)
