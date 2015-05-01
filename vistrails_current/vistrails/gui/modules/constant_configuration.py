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
""" This file specifies the configuration widget for Constant
modules. Please notice that this is different from the module configuration
widget described in module_configure.py. We present a Color constant to be
used as a template for creating a configuration widget for other custom
constants.

"""

from PyQt4 import QtCore, QtGui
from vistrails.core.utils import any, expression, versions_increasing
from vistrails.core import system
from vistrails.gui.theme import CurrentTheme

import os

############################################################################

def setPlaceholderTextCompat(self, value):
    """ Qt pre 4.7.0 does not have setPlaceholderText
    """
    if versions_increasing(QtCore.QT_VERSION_STR, '4.7.0'):
        self.setText(value)
    else:
        self.setPlaceholderText(value)

class ConstantWidgetMixin(object):

    def __init__(self, contents=None):
        self._last_contents = contents

    def update_parent(self):
        newContents = self.contents()
        if newContents != self._last_contents:
            if self.parent() and hasattr(self.parent(), 'updateMethod'):
                self.parent().updateMethod()
            self._last_contents = newContents
            self.emit(QtCore.SIGNAL('contentsChanged'), (self, newContents))

    def setDefault(self, strValue):
        pass

class StandardConstantWidgetBase(ConstantWidgetMixin):
    """
    StandardConstantWidget is a basic widget to be used
    to edit int/float/string values in VisTrails.

    When creating your own widget, you can subclass from this widget if you
    need only a QLineEdit or use your own QT widget. There are two things you
    need to pay attention to:

    1) Re-implement the contents() method so we can get the current value
       stored in the widget.

    2) When the user is done with configuration, make sure to call
       update_parent() so VisTrails can pass that information to the Provenance
       System. In this example we do that on focusOutEvent and when the user
       presses the return key.

    """
    def __new__(cls, *args, **kwargs):
        param = None
        if len(args) > 0:
            param = args[0]
        if 'param' in kwargs:
            param = kwargs['param']
        if param is None:
            raise ValueError("Must pass param as first argument.")
        if param.port_spec_item and param.port_spec_item.entry_type and \
                param.port_spec_item.entry_type.startswith("enum"):
            return StandardConstantEnumWidget.__new__(StandardConstantEnumWidget, *args, **kwargs)
        return StandardConstantWidget.__new__(StandardConstantWidget, *args, **kwargs)

    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)

        Initialize the line edit with its contents. Content type is limited
        to 'int', 'float', and 'string'

        """

        psi = param.port_spec_item
        if param.strValue:
            value = param.strValue
        elif psi and psi.default:
            value = psi.default
        else:
            value = param.strValue
        ConstantWidgetMixin.__init__(self, value)

        # assert param.namespace == None
        # assert param.identifier == 'org.vistrails.vistrails.basic'
        if psi and psi.default:
            self.setDefault(psi.default)
        contents = param.strValue
        contentType = param.type
        if contents: # do not replace old default value with empty value
            self.setText(contents)
        self._contentType = contentType

    def setDefault(self, default):
        # Implement this in a subclass!
        pass

    def contents(self):
        """contents() -> str
        Re-implement this method to make sure that it will return a string
        representation of the value that it will be passed to the module
        As this is a QLineEdit, we just call text()

        """
        self.update_text()
        return str(self.text())

    def setContents(self, strValue, silent=True):
        """setContents(strValue: str) -> None
        Re-implement this method so the widget can change its value after 
        constructed. If silent is False, it will propagate the event back 
        to the parent.
        As this is a QLineEdit, we just call setText(strValue)
        """
        self.setText(strValue)
        self.update_text()
        if not silent:
            self.update_parent()
            
    def update_text(self):
        """ update_text() -> None
        Update the text to the result of the evaluation

        """
        # FIXME: eval should pretty much never be used
        base = expression.evaluate_expressions(self.text())
        if self._contentType == 'String':
            self.setText(base)
        else:
            try:
                self.setText(str(eval(str(base), None, None)))
            except:
                self.setText(base)


class StandardConstantWidget(QtGui.QLineEdit, StandardConstantWidgetBase):
    def __init__(self, param, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        StandardConstantWidgetBase.__init__(self, param, parent)
        self.connect(self,
                     QtCore.SIGNAL('returnPressed()'),
                     self.update_parent)

    def setDefault(self, value):
        setPlaceholderTextCompat(self, value)

    def sizeHint(self):
        metrics = QtGui.QFontMetrics(self.font())
        width = min(metrics.width(self.text())+10,70)
        return QtCore.QSize(width, 
                            metrics.height()+6)
    
    def minimumSizeHint(self):
        return self.sizeHint()

    ###########################################################################
    # event handlers

    def focusInEvent(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent

        """
        self._contents = str(self.text())
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        QtGui.QLineEdit.focusInEvent(self, event)

    def focusOutEvent(self, event):
        self.update_parent()
        QtGui.QLineEdit.focusOutEvent(self, event)
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)


class BaseStringWidget(object): # < virtual QtGui.QWidget
    def focusInEvent(self, event):
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        super(BaseStringWidget, self).focusInEvent(event)

    def focusOutEvent(self, event):
        self.parent().update_parent()
        super(BaseStringWidget, self).focusOutEvent(event)
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)


class SingleLineStringWidget(BaseStringWidget, QtGui.QLineEdit):
    def __init__(self, parent, contents="", default=""):
        QtGui.QLineEdit.__init__(self, contents, parent)
        self.setDefault(default)

        self.connect(self,
                     QtCore.SIGNAL('returnPressed()'),
                     parent.update_parent)

    def setContents(self, contents):
        self.setText(expression.evaluate_expressions(contents))

    def contents(self):
        contents = expression.evaluate_expressions(unicode(self.text()))
        self.setText(contents)
        return contents

    def setDefault(self, value):
        setPlaceholderTextCompat(self, value)

    def sizeHint(self):
        metrics = QtGui.QFontMetrics(self.font())
        width = min(metrics.width(self.text()) + 10, 70)
        return QtCore.QSize(width,
                            metrics.height() + 6)

    def minimumSizeHint(self):
        return self.sizeHint()


class MultiLineStringWidget(BaseStringWidget, QtGui.QTextEdit):
    def __init__(self, parent, contents="", default=""):
        QtGui.QTextEdit.__init__(self, parent)
        self.setPlainText(contents)
        self.setAcceptRichText(False)
        self.setDefault(default)

    def setContents(self, contents):
        self.setPlainText(expression.evaluate_expressions(contents))

    def contents(self):
        contents = expression.evaluate_expressions(unicode(self.toPlainText()))
        self.setPlainText(contents)
        return contents

    def setDefault(self, value):
        pass # TODO : some magic will be required for this

    def sizeHint(self):
        metrics = QtGui.QFontMetrics(self.font())
        width = 70
        return QtCore.QSize(width,
                            (metrics.height() + 1) * 3 + 5)

    def minimumSizeHint(self):
        return self.sizeHint()


class StringWidget(QtGui.QWidget, ConstantWidgetMixin):
    def __new__(cls, *args, **kwargs):
        param = None
        if len(args) > 0:
            param = args[0]
        if 'param' in kwargs:
            param = kwargs['param']
        if param is None:
            raise ValueError("Must pass param as first argument.")
        if param.port_spec_item and param.port_spec_item.entry_type and \
                param.port_spec_item.entry_type.startswith("enum"):
            # StandardConstantEnumWidget is not related to StringWidget, so
            # we have to call __init__ as well before returning
            # That's why there's no __new__ here
            return StandardConstantEnumWidget(*args, **kwargs)
        return QtGui.QWidget.__new__(cls, *args, **kwargs)

    def __init__(self, param, parent=None):
        QtGui.QWidget.__init__(self)
        self.setLayout(QtGui.QHBoxLayout())
        self.layout().setMargin(5)
        self.layout().setSpacing(5)

        self._widget = None
        self._multiline = None
        self._default = ""

        self._button = QtGui.QToolButton()
        self._button.setIcon(CurrentTheme.MULTILINE_STRING_ICON)
        self._button.setIconSize(QtCore.QSize(12, 12))
        self._button.setToolTip("Toggle multi-line editor")
        self._button.setAutoRaise(True)
        self._button.setSizePolicy(QtGui.QSizePolicy(
                QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed))
        self._button.setCheckable(True)
        self.connect(self._button, QtCore.SIGNAL('toggled(bool)'),
                     self.switch_multiline)
        self.layout().addWidget(self._button)

        psi = param.port_spec_item
        if param.strValue:
            value = param.strValue
        elif psi and psi.default:
            value = psi.default
        else:
            value = param.strValue
        ConstantWidgetMixin.__init__(self, value)

        # assert param.namespace == None
        # assert param.identifier == 'edu.utah.sci.vistrails.basic'
        if psi and psi.default:
            self.setDefault(psi.default)
        contents = param.strValue
        self.setContents(contents)

    def switch_multiline(self, multiline):
        if multiline != self._multiline:
            # Doing multiline -> not multiline while the widget contains
            # line-returns is weird but won't cause loss of data, so I'm not
            # explicitely disabling it
            # Not that the multiline widget will pop up again next time if the
            # user doesn't change the contents
            self.setContents(self.contents(), multiline=multiline)

    def setDefault(self, value):
        self._default = value
        if self._widget is not None:
            self._widget.setDefault(value)

    def contents(self):
        return self._widget.contents()

    def setContents(self, strValue, silent=True, multiline=None):
        if multiline is None:
            multiline = '\n' in strValue
        if self._multiline is not multiline:
            self._multiline = multiline
            if self._widget is not None:
                self._widget.deleteLater()
            if not multiline:
                self._widget = SingleLineStringWidget(self,
                                                      strValue, self._default)
            else:
                self._widget = MultiLineStringWidget(self,
                                                     strValue, self._default)
            self._button.setChecked(multiline)
            self.layout().insertWidget(0, self._widget)
            self.updateGeometry()
        else:
            self._widget.setContents(strValue)

        if not silent:
            self.update_parent()

    def changeEvent(self, event):
        """ Hide button when in read-only mode
        
        """
        if event.type() == QtCore.QEvent.EnabledChange:
            self._button.setVisible(self.isEnabled())
        return QtGui.QWidget.changeEvent(self, event)

    ###########################################################################
    # event handlers

    def focusInEvent(self, event):
        #self._contents = str(self.contents())
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        super(StringWidget, self).focusInEvent(event)

    def focusOutEvent(self, event):
        self.update_parent()
        super(StringWidget, self).focusOutEvent(event)
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)


class StandardConstantEnumWidget(QtGui.QComboBox, StandardConstantWidgetBase):
    def __init__(self, param, parent=None):
        QtGui.QComboBox.__init__(self, parent)
        psi = param.port_spec_item
        if psi and psi.entry_type == 'enumFree':
            self.setEditable(True)
            self.setInsertPolicy(QtGui.QComboBox.NoInsert)
            self.connect(self.lineEdit(),
                         QtCore.SIGNAL('returnPressed()'),
                         self.update_parent)
        self.addItems(psi.values)
        if psi and (psi.entry_type == "enumEmpty" or 
                    psi.entry_type == 'enumFree'):
            self.setCurrentIndex(-1)
        StandardConstantWidgetBase.__init__(self, param, parent)
        self.connect(self,
                     QtCore.SIGNAL('currentIndexChanged(int)'),
                     self.update_parent)

    def text(self):
        return self.currentText()

    def setText(self, text):
        idx = self.findText(text)
        if idx > -1:
            self.setCurrentIndex(idx)
            if self.isEditable():
                self.lineEdit().setText(text)
        elif self.isEditable():
            self.lineEdit().setText(text)

    def setDefault(self, value):
        idx = self.findText(value)
        if idx > -1:
            self.setCurrentIndex(idx)
            if self.isEditable():
                setPlaceholderTextCompat(self.lineEdit(), value)
        elif self.isEditable():
            setPlaceholderTextCompat(self.lineEdit(), value)


    ###########################################################################
    # event handlers

    def focusInEvent(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent

        """
        self._contents = str(self.text())
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        QtGui.QComboBox.focusInEvent(self, event)

    def focusOutEvent(self, event):
        self.update_parent()
        QtGui.QComboBox.focusOutEvent(self, event)
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)


###############################################################################
# File Constant Widgets

class PathChooserToolButton(QtGui.QToolButton):
    """
    PathChooserToolButton is a toolbar button that opens a browser for
    paths.  The lineEdit is updated with the pathname that is selected.

    """
    def __init__(self, parent=None, lineEdit=None, toolTip=None):
        """
        PathChooserToolButton(parent: QWidget, 
                              lineEdit: StandardConstantWidget) ->
                 PathChooserToolButton

        """
        QtGui.QToolButton.__init__(self, parent)
        self.setIcon(QtGui.QIcon(
                self.style().standardPixmap(QtGui.QStyle.SP_DirOpenIcon)))
        self.setIconSize(QtCore.QSize(12,12))
        if toolTip is None:
            toolTip = 'Open a file chooser'
        self.setToolTip(toolTip)
        self.setAutoRaise(True)
        self.lineEdit = lineEdit
        self.connect(self,
                     QtCore.SIGNAL('clicked()'),
                     self.runDialog)

    def setPath(self, path):
        """
        setPath() -> None

        """
        if self.lineEdit and path:
            self.lineEdit.setText(path)
            self.lineEdit.update_parent()
            self.parent().update_parent()
    
    def openChooser(self):
        text = self.lineEdit.text() or system.vistrails_data_directory()
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Use Filename '
                                                     'as Value...',
                                                     text,
                                                     'All files '
                                                     '(*.*)')
        if not fileName:
            return None
        filename = os.path.abspath(str(QtCore.QFile.encodeName(fileName)))
        dirName = os.path.dirname(filename)
        system.set_vistrails_data_directory(dirName)
        return filename

    def runDialog(self):
        path = self.openChooser()
        self.setPath(path)

class PathChooserWidget(QtGui.QWidget, ConstantWidgetMixin):
    """
    PathChooserWidget is a widget containing a line edit and a button that
    opens a browser for paths. The lineEdit is updated with the pathname that is
    selected.

    """    
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
        parent: QWidget)
        Initializes the line edit with contents

        """
        QtGui.QWidget.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        layout = QtGui.QHBoxLayout()
        self.line_edit = StandardConstantWidget(param, self)
        self.browse_button = self.create_browse_button()
        layout.setMargin(5)
        layout.setSpacing(5)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.browse_button)
        self.setLayout(layout)

    def create_browse_button(self):
        return PathChooserToolButton(self, self.line_edit)

    def updateMethod(self):
        if self.parent() and hasattr(self.parent(), 'updateMethod'):
            self.parent().updateMethod()

    def contents(self):
        """contents() -> str
        Return the contents of the line_edit

        """
        return self.line_edit.contents()
    
    def setContents(self, strValue, silent=True):
        """setContents(strValue: str) -> None
        Updates the contents of the line_edit 
        """
        self.line_edit.setContents(strValue, silent)
        if not silent:
            self.update_parent()
 
        
    def focusInEvent(self, event):
        """ focusInEvent(event: QEvent) -> None
        Pass the event to the parent

        """
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)
        QtGui.QWidget.focusInEvent(self, event)   
        
    def focusOutEvent(self, event):
        self.update_parent()
        QtGui.QWidget.focusOutEvent(self, event)
        if self.parent():
            QtCore.QCoreApplication.sendEvent(self.parent(), event)

class FileChooserToolButton(PathChooserToolButton):
    def __init__(self, parent=None, lineEdit=None):
        PathChooserToolButton.__init__(self, parent, lineEdit, 
                                       "Open a file chooser")
        
    def openChooser(self):
        text = self.lineEdit.text() or system.vistrails_data_directory()
        fileName = QtGui.QFileDialog.getOpenFileName(self,
                                                     'Use Filename '
                                                     'as Value...',
                                                     text,
                                                     'All files '
                                                     '(*.*)')
        if not fileName:
            return None
        filename = os.path.abspath(str(QtCore.QFile.encodeName(fileName)))
        dirName = os.path.dirname(filename)
        system.set_vistrails_data_directory(dirName)
        return filename


class FileChooserWidget(PathChooserWidget):
    def create_browse_button(self):
        return FileChooserToolButton(self, self.line_edit)


class DirectoryChooserToolButton(PathChooserToolButton):
    def __init__(self, parent=None, lineEdit=None):
        PathChooserToolButton.__init__(self, parent, lineEdit, 
                                       "Open a directory chooser")

    def openChooser(self):
        text = self.lineEdit.text() or system.vistrails_data_directory()
        fileName = QtGui.QFileDialog.getExistingDirectory(self,
                                                          'Use Directory '
                                                          'as Value...',
                                                          text)
        if not fileName:
            return None
        filename = os.path.abspath(str(QtCore.QFile.encodeName(fileName)))
        dirName = os.path.dirname(filename)
        system.set_vistrails_data_directory(dirName)
        return filename


class DirectoryChooserWidget(PathChooserWidget):
    def create_browse_button(self):
        return DirectoryChooserToolButton(self, self.line_edit)

class OutputPathChooserToolButton(PathChooserToolButton):
    def __init__(self, parent=None, lineEdit=None):
        PathChooserToolButton.__init__(self, parent, lineEdit,
                                       "Open a path chooser")
    
    def openChooser(self):
        text = self.lineEdit.text() or system.vistrails_data_directory()
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                     'Save Path',
                                                     text,
                                                     'All files (*.*)')
        if not fileName:
            return None
        filename = os.path.abspath(str(QtCore.QFile.encodeName(fileName)))
        dirName = os.path.dirname(filename)
        system.set_vistrails_data_directory(dirName)
        return filename

class OutputPathChooserWidget(PathChooserWidget):
    def create_browse_button(self):
        return OutputPathChooserToolButton(self, self.line_edit)

class BooleanWidget(QtGui.QCheckBox, ConstantWidgetMixin):

    _values = ['True', 'False']
    _states = [QtCore.Qt.Checked, QtCore.Qt.Unchecked]

    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)
        Initializes the line edit with contents
        """
        QtGui.QCheckBox.__init__(self, parent)

        psi = param.port_spec_item
        if param.strValue:
            value = param.strValue
        elif psi and psi.default:
            value = psi.default
        else:
            value = param.strValue
        ConstantWidgetMixin.__init__(self, value)

        if psi and psi.default:
            self.setDefault(psi.default)
        if param.strValue:
            self.setContents(param.strValue)

        self._silent= False
        self.connect(self, QtCore.SIGNAL('stateChanged(int)'),
                     self.change_state)
        
    def contents(self):
        return self._values[self._states.index(self.checkState())]

    def setContents(self, strValue, silent=True):
        if not strValue:
            return

        assert strValue in self._values
        if silent:
            self._silent = True
        self.setCheckState(self._states[self._values.index(strValue)])
        if not silent:
            self.update_parent()
        self._silent = False

    def setDefault(self, strValue):
        self.setContents(strValue)

    def change_state(self, state):
        if not self._silent:
            self.update_parent()

###############################################################################
# Constant Color widgets

class ColorChooserButton(QtGui.QPushButton):
    def __init__(self, parent=None):
        QtGui.QPushButton.__init__(self, parent)
        # self.setFrameStyle(QtGui.QFrame.Box | QtGui.QFrame.Plain)
        # self.setAttribute(QtCore.Qt.WA_PaintOnScreen)
        self.setFlat(True)
        self.setAutoFillBackground(True)
        self.setColor(QtGui.QColor(255,255,255))
        self.setFixedSize(30,22)
        if system.systemType == 'Darwin':
            #the mac's nice look messes up with the colors
            self.setAttribute(QtCore.Qt.WA_MacMetalStyle, False)
        self.clicked.connect(self.openChooser)

    def setColor(self, qcolor, silent=True):
        self.qcolor = qcolor
        self.setStyleSheet("border: 1px solid black; "
                           "background-color: rgb(%d, %d, %d);" %
                           (qcolor.red(), qcolor.green(), qcolor.blue()))
        self.repaint()
        if not silent:
            self.emit(QtCore.SIGNAL("color_selected"))

    def sizeHint(self):
        return QtCore.QSize(24,24)

    def openChooser(self):
        """
        openChooser() -> None

        """
        color = QtGui.QColorDialog.getColor(self.qcolor, self.parent())
        if color.isValid():
            self.setColor(color, silent=False)
        else:
            self.setColor(self.qcolor)


class ColorWidget(QtGui.QWidget, ConstantWidgetMixin):
    def __init__(self, param, parent=None):
        """__init__(param: core.vistrail.module_param.ModuleParam,
                    parent: QWidget)
        """
        psi = param.port_spec_item
        if not param.strValue and psi and psi.default:
            contents = psi.default
            self._is_default = True
        else:
            contents = param.strValue
            self._is_default = not contents
        QtGui.QWidget.__init__(self, parent)
        ConstantWidgetMixin.__init__(self, param.strValue)
        layout = QtGui.QHBoxLayout()
        self.color_indicator = ColorChooserButton(self)
        self.connect(self.color_indicator,
                     QtCore.SIGNAL("color_selected"),
                     self.update_parent)
        self._last_contents = contents
        layout.setMargin(5)
        layout.setSpacing(5)
        layout.addWidget(self.color_indicator)
        layout.addStretch(1)
        self.setLayout(layout)
        self.setContents(contents)
        
    def contents(self):
        """contents() -> str
        Return the string representation of color_indicator

        """
        return "%s,%s,%s" % (self.color_indicator.qcolor.redF(),
                             self.color_indicator.qcolor.greenF(),
                             self.color_indicator.qcolor.blueF())
        
    def setContents(self, strValue, silent=True):
        """setContents(strValue: str) -> None
        Updates the color_indicator to display the color in strValue
        
        """
        if strValue != '':
            color = strValue.split(',')
            qcolor = QtGui.QColor(float(color[0])*255,
                                  float(color[1])*255,
                                  float(color[2])*255)
            self.color_indicator.setColor(qcolor, silent)
        self._is_default = False

    def setDefault(self, strValue):
        if self._is_default:
            self.setContents(strValue, True)
            self._is_default = True
