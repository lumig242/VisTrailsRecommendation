###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################
from vistrails.core import modules
from vistrails.core.common import *
from vistrails.core.data_structures.bijectivedict import Bidict
from vistrails.core.modules.vistrails_module import ModuleConnector, ModuleError
from vistrails.core.utils import DummyView
import copy
import vistrails.core.interpreter.base
import vistrails.core.interpreter.utils
import vistrails.core.vistrail.pipeline
import atexit

# from core.modules.module_utils import FilePool

################################################################################

class Interpreter(vistrails.core.interpreter.cached.CachedInterpreter):

    def clean_non_cacheable_modules(self):
        non_cacheable_modules = [i for
                                 (i, mod) in self._objects.iteritems()]
        self.clean_modules(non_cacheable_modules)

    __instance = None
    @staticmethod
    def get():
        if not Interpreter.__instance:
            instance = Interpreter()
            Interpreter.__instance = instance
            def cleanup():
                instance._file_pool.cleanup()
            atexit.register(cleanup)
        return Interpreter.__instance
        

################################################################################
