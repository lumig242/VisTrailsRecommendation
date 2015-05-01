#Copied imports from HTTP package init.py file
from PyQt4 import QtGui
#Edited this line to include Module at the end
from core.modules.vistrails_module import Module, ModuleError
from core.configuration import get_vistrails_persistent_configuration
from gui.utils import show_warning
import core.modules.vistrails_module
import core.modules
import core.modules.basic_modules
import core.modules.module_registry
import core.system
from core import debug

from component_search_form import *

from component_search_form import ComponentSearchForm
from networkx_graph import TestForm

identifier = 'edu.cmu.sv.componentSearch'
name = 'Recommendation'
version = '1.0.0'

component_search_form = ComponentSearchForm()

class AbstractModule(Module):
    def __init__(self):
        Module.__init__(self)
        print 'test'

def initialize(*args, **keywords):
    reg = core.modules.module_registry.get_module_registry()
    basic = core.modules.basic_modules
    
    reg.add_module(AbstractModule)
    reg.add_input_port(AbstractModule, "Intended Input Data Type", (basic.String, 'Intended Input Data Type'))
    reg.add_output_port(AbstractModule, "Intended Output Data Type",
                        (basic.String, 'Intended Output Data Type'))
#    desc = reg.get_descriptor(AbstractModule)
#    print desc.identifier
#    reg.delete_module(desc.identifier, AbstractModule)
    
def menu_items():
    """menu_items() -> tuple of (str,function)
    It returns a list of pairs containing text for the menu and a
    callback function that will be executed when that menu item is selected.
    """
    def show_search_form():
        component_search_form.show_main_window()

    lst = []
    lst.append(("Start Recommendation Engine", show_search_form))
    return tuple(lst)
