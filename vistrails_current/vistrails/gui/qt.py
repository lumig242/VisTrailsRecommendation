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
"""The only reason this module exists is to try to prevent QObjects
from being created before a QApplication gets constructed. The problem
with a QObject being constructed before a QApplication is that signals
and slots do not get connected, leading to hard-to-spot bugs.

Notice that there is no hard enforcement - if the client code does not
ask for permission, nothing stops it from creating QObjects (which
won't work correctly). Even worse, nothing stops a malicious object
from setting okToCreateQObjects directly.

As the python saying goes, 'we are all consenting adults here'."""

import inspect
from PyQt4 import QtGui, QtCore
import types

################################################################################

class qt_super(object):

    def __init__(self, class_, obj):
        self._class = class_
        self._obj = obj

    def __getattr__(self, attr):
        s = super(self._class, self._obj)
        try:
            return getattr(s, attr)
        except AttributeError, e:
            mro = type(self._obj).mro()
            try:
                ix = mro.index(self._class)
            except ValueError:
                raise TypeError("qt_super: obj must be an instance of class")
            
            for class_ in mro[ix+1:]:
                try:
                    unbound_meth = getattr(class_, attr)
                    return types.MethodType(unbound_meth, self._obj, class_)
                except AttributeError:
                    pass
            raise e

################################################################################

class DisallowedCaller(Exception):
    """This expection is raised whenever a caller that's not privileged to
allow QObject construction tries to do so."""
    def __str__(self):
        return "Caller is not allowed to call this function"

class QApplicationNotYetCreated(Exception):
    """This expection is raised whenever a function asks for permission to
create a QObject but the QApplication has not granted it yet."""
    def __str__(self):
        return "QApplication has not been created yet"

def allowQObjects():
    """Allows subsequent QObject creation. The constructor for the
QApplication-derived class must call this so that we know it's alright
to start creating other QtCore.QObjects."""
    
    # tries to check if caller is allowed to call this
    caller = inspect.currentframe().f_back
    d = caller.f_locals
    if (not d.has_key('self') or
        not isinstance(d['self'], QtCore.QCoreApplication)):
        raise DisallowedCaller
    global okToCreateQObjects
    okToCreateQObjects = True

def askForQObjectCreation():
    """This function simply throws an exception if it is not yet ok
to create QObjects."""
    global okToCreateQObjects
    if not okToCreateQObjects:
        raise QApplicationNotYetCreated()

global _appHolder
_appHolder = None

def createBogusQtGuiApp(argv=["bogus"]):    
    """createBogusQtGuiApp creates a bogus QtApplication so we can
    create qobjects during test runs.
    """    
    class BogusApplication(QtGui.QApplication):
        def __init__(self):
            QtGui.QApplication.__init__(self, argv)
            allowQObjects()
    global _appHolder
    if QtGui.qApp:
        _appHolder = QtGui.qApp
    if not _appHolder:
        _appHolder = BogusApplication()
    return _appHolder

def destroyBogusQtApp():
    global _appHolder
    del _appHolder

def qt_version():
    return [int(i)
            for i in
            QtCore.qVersion().split('.')]

################################################################################

okToCreateQObjects = False

class SignalSet(object):
    
    """SignalSet stores a list of (object, signal, method) that can be
    all connected and disconnected simultaneously. This way, it's
    harder to forget to disconnect one of many signals. Also, if the
    SignalSet has already been plugged, it will signal an exception,
    to avoid multiple connections."""
    
    def __init__(self, owner, signalTripleList):
        self.owner = owner
        self.signalTripleList = signalTripleList
        self.plugged = False

    def plug(self):
        if self.plugged:
            raise ValueError("SignalSet %s is already plugged" % self)
        for tupl in self.signalTripleList:
            self.owner.connect(*tupl)
        self.plugged = True

    def unplug(self):
        if not self.plugged:
            return
        for tupl in self.signalTripleList:
            self.owner.disconnect(*tupl)
        self.plugged = False

        
################################################################################

_oldConnect = QtCore.QObject.connect
_oldDisconnect = QtCore.QObject.disconnect
_oldEmit = QtCore.QObject.emit

def _wrapConnect(callableObject):
    """Returns a wrapped call to the old version of QtCore.QObject.connect"""
    @staticmethod
    def call(*args):
        callableObject(*args)
        _oldConnect(*args)
    return call

def _wrapDisconnect(callableObject):
    """Returns a wrapped call to the old version of QtCore.QObject.disconnect"""
    @staticmethod
    def call(*args):
        callableObject(*args)
        _oldDisconnect(*args)
    return call

def enableSignalDebugging(**kwargs):
    """Call this to enable Qt Signal debugging. This will trap all
    connect, disconnect and emit calls. For example:

    enableSignalDebugging(connectCall=callable1, disconnectCall=callable2,
                          emitCall=callable3)

    will call callable1, 2 and 3 when the respective Qt methods are issued.
    """

    f = lambda *args: None
    connectCall = kwargs.get('connectCall', f)
    disconnectCall = kwargs.get('disconnectCall', f)
    emitCall = kwargs.get('emitCall', f)

    def printIt(msg):
        def call(*args):
            print msg, args
        return call
    QtCore.QObject.connect = _wrapConnect(connectCall)
    QtCore.QObject.disconnect = _wrapDisconnect(disconnectCall)

    def new_emit(self, *args):
        emitCall(self, *args)
        _oldEmit(self, *args)

    QtCore.QObject.emit = new_emit
