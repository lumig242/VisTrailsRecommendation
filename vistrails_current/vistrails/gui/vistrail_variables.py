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
""" This file describes the vistrail variables box into which the user can
drop constants from the module palette

"""
from PyQt4 import QtCore, QtGui
from vistrails.gui.variable_dropbox import QVariableDropBox
from vistrails.gui.common_widgets import QToolWindowInterface
from vistrails.gui.vistrails_palette import QVistrailsPaletteInterface

################################################################################

class QVistrailVariables(QVariableDropBox, QVistrailsPaletteInterface):
    """
    QVistrailVariables shows variables associated with a vistrail, and
    supports drag/drop actions of constant items from the module palette
    
    """
    def __init__(self, parent=None):
        """ QVistrailVariables(parent: QWidget) -> QVistrailVariables
        Initialize widget constraints
        
        """
        QVariableDropBox.__init__(self, parent)
        self.setWindowTitle('Vistrail Variables')
        self.setToolWindowAcceptDrops(True)

    def sizeHint(self):
        """ sizeHint() -> None
        """
        return QtCore.QSize(self.size().width(), 300)

