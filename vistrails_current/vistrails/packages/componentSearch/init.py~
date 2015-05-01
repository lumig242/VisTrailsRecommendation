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
    
