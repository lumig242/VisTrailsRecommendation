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
import webbrowser

from cmac_form import *

class TwoDimVariableMap(Module):
    def __init__(self):
        Module.__init__(self)
    def compute(self):
        webbrowser.open('http://einstein.sv.cmu.edu:9003/cmac/web/twoDimMap.html')

class TwoDimZonalMean(Module):
    def __init__(self):
        Module.__init__(self)
    def compute(self):
        webbrowser.open('http://einstein.sv.cmu.edu:9003/cmac/web/twoDimZonalMean.html')

class TwoDimTimeSeries(Module):
    def __init__(self):
        Module.__init__(self)
    def compute(self):
        webbrowser.open('http://einstein.sv.cmu.edu:9003/cmac/web/twoDimTimeSeries.html')

class ThreeDimVarTwoDimSlice(Module):
    def __init__(self):
        Module.__init__(self)
    def compute(self):
        webbrowser.open('http://einstein.sv.cmu.edu:9003/cmac/web/twoDimSlice3D.html')

class ThreeDimVarZonalMean(Module):
    def __init__(self):
        Module.__init__(self)
    def compute(self):
        webbrowser.open('http://einstein.sv.cmu.edu:9003/cmac/web/threeDimZonalMean.html')
        
class ThreeDimVarVerticalProfile(Module):
    def __init__(self):
        Module.__init__(self)
    def compute(self):
        webbrowser.open('http://einstein.sv.cmu.edu:9003/cmac/web/threeDimVarVertical.html')

class ScatterHistogram(Module):
    def __init__(self):
        Module.__init__(self)
    def compute(self):
        webbrowser.open('http://einstein.sv.cmu.edu:9003/cmac/web/scatterPlot2Vars.html')

class DiffPlot(Module):
    def __init__(self):
        Module.__init__(self)
    def compute(self):
        webbrowser.open('http://einstein.sv.cmu.edu:9003/cmac/web/diffPlot2Vars.html')

class ConditionalSampling(Module):
    def __init__(self):
        Module.__init__(self)
    def compute(self):
        webbrowser.open('http://einstein.sv.cmu.edu:9003/cmac/web/conditionalSampling.html')

def initialize(*args, **keywords):
    reg = core.modules.module_registry.get_module_registry()
    basic = core.modules.basic_modules
    
    reg.add_module(TwoDimVariableMap)
    reg.add_module(TwoDimZonalMean)
    reg.add_module(TwoDimTimeSeries)
    reg.add_module(ThreeDimVarTwoDimSlice)
    reg.add_module(ThreeDimVarZonalMean)
    reg.add_module(ThreeDimVarVerticalProfile)
    reg.add_module(ScatterHistogram)
    reg.add_module(DiffPlot)
    reg.add_module(ConditionalSampling)
#    desc = reg.get_descriptor(AbstractModule)
#    print desc.identifier
#    reg.delete_module(desc.identifier, AbstractModule)
    
