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
import logging
import logging.handlers
import inspect
import os
import os.path
import re
import time
import vistrails.core

# from core.utils import VersionTooLow
# from core import system

################################################################################

_warningformat = re.compile(
        '^(.+):'
        '([0-9]+): '
        '([A-Za-z_][A-Za-z0-9_]*): '
        '((?:.|\n)+)$')

class EmitWarnings(logging.Handler):
    """A logging Handler that re-logs warning messages in our log format.

    This parses the warnings logged by the standard `warnings` module and
    writes them to the given logger at level WARNING in the format we use
    (see DebugPrint#message()).
    """
    def __init__(self, logger):
        logging.Handler.__init__(self)
        self.logger = logger

    def emit(self, record):
        # Here we basically do the contrary of warnings:formatwarning()
        m = _warningformat.match(record.args[0])
        if m == None:
            self.logger.warning("(File info not available)\n" +
                           record.args[0])
        else:
            filename, lineno, category, message = m.groups()
            # And here we do self.message()
            self.logger.warning('%s, line %s\n%s: %s' % (filename, lineno,
                                                    category, message))

################################################################################

class DebugPrint:
    """ Class to be used for debugging information.

    Verboseness can be set in the following way:
        - DebugPrint.CRITICAL
            Only critical messages will be shown
        - DebugPrint.WARNING
            Warnings and critical messages will be shown (default)
        - DebugPrint.INFO
            Information, warning and Critical messages will be shown (verbose)
        - DebugPrint.DEBUG
            All logging messages will be shown (extra verbose)

    It uses information such as file name and line number only when printing
    to files and consoles, a stream can be registered to be used in gui.debug.
    Also, it goes up only one level in the traceback stack,
    so it will only get information of who called the DebugPrint functions.

    Example of usage:
        >>> from core import debug
        >>> debug.DebugPrint.getInstance().set_message_level(
                    debug.DebugPrint.WARNING)
        # the following messages will be shown
        >>> debug.critical('This is an error message')
        >>> debug.warning('This is a warning message')
        # only warnings and above are shown
        >>> debug.log('This is a log message and it will not be shown')

    """
    (CRITICAL, WARNING, INFO, DEBUG) = (logging.CRITICAL,
                                       logging.WARNING,
                                       logging.INFO,
                                       logging.DEBUG) # python logging levels
    #Singleton technique
    _instance = None
    class DebugPrintSingleton():
        def __call__(self, *args, **kw):
            if DebugPrint._instance is None:
                obj = DebugPrint(*args, **kw)
                DebugPrint._instance = obj
            return DebugPrint._instance

    getInstance = DebugPrintSingleton()

    def make_logger(self, f=None):
        self.fhandler = None
        """self.make_logger_240(file) -> logger. Creates a logging object to
        be used within the DebugPrint class that sends the debugging
        output to file.
        We will configure log so it outputs to both stderr and a file.

        """
        # Setup root logger
        self.logger = logging.getLogger('VisLog')
        self.logger.setLevel(logging.DEBUG)
        self.format = logging.Formatter("%(asctime)s %(levelname)s:\n%(message)s")

        # Setup warnings logger
        if hasattr(logging, 'captureWarnings'):
            wlogger = logging.getLogger('py.warnings')
            wlogger.propagate = False
            wlogger.addHandler(EmitWarnings(self.logger))
            logging.captureWarnings(True)

        # first we define a handler for logging to a file
        if f:
            self.set_logfile(f)

        #then we define a handler to log to the console
        self.console = logging.StreamHandler()
        self.console.setFormatter(self.format)
        self.console.setLevel(logging.WARNING)
        self.logger.addHandler(self.console)

#    if system.python_version() <= (2,4,0,'',0):
#        raise VersionTooLow('Python', '2.4.0')

    def __init__(self):
        self.make_logger()
        self.app = None

    def set_logfile(self, f):
        """set_logfile(file) -> None. Redirects debugging
        output to file."""
        if f is None:
            if self.fhandler:
                self.logger.removeHandler(self.fhandler)
                self.fhandler = None
            return

        def rotate_file_if_necessary(filename):
            statinfo = os.stat(filename)
            if statinfo.st_size > 1024*1024:
                #rotate file
                mincount = 1
                maxcount = 5
                count = maxcount
                newfile = "%s.%s"%(filename, count)
                while not os.path.exists(newfile) and count >= mincount:
                    count = count - 1
                    newfile = "%s.%s"%(filename, count)
                if count == 5:
                    os.unlink("%s.%s"%(filename, count))
                    count = 4
                while count >= mincount:
                    os.rename("%s.%s"%(filename, count), "%s.%s"%(filename, count+1))
                    count = count -1
                os.rename(filename, "%s.%s"%(filename, mincount))

        try:
            # there's a problem on Windows with RotatingFileHandler and that
            # happens when VisTrails starts child processes (it seems related
            # to the way Windows manages file handlers)
            # see http://bugs.python.org/issue4749
            # in this case we will deal with log files differently on Windows:
            # we will check if we need to rotate the file at the beginning of
            # the session.
            import vistrails.core.system
            if vistrails.core.system.systemType in ["Windows", "Microsoft"]:
                if not os.path.exists(f):
                    open(f,'w').close()
                rotate_file_if_necessary(f)
                handler = logging.FileHandler(f)
            else:
                handler = logging.handlers.RotatingFileHandler(f, maxBytes=1024*1024,
                                                               backupCount=5)
            handler.setFormatter(self.format)
            handler.setLevel(logging.DEBUG)
            if self.fhandler:
                self.logger.removeHandler(self.fhandler)
            self.fhandler = handler
            self.logger.addHandler(handler)

        except Exception, e:
            self.critical("Could not set log file %s: %s"%(f,str(e)))

    def set_message_level(self,level):
        """self.set_message_level(level) -> None. Sets the logging
        verboseness.  level must be one of (DebugPrint.CRITICAL,
        DebugPrint.WARNING, DebugPrint.INFO, DebugPrint.DEBUG)."""
        self.console.setLevel(level)

    def register_splash(self, app):
        """ register_splash(self, classname)
        Registers a method splashMessage(message)
        """
        self.app = app

    def splashMessage(self, msg):
        """ splashMessage(self, string)
        Writes a splashmessage if app is registered
        """
        if self.app:
            self.app.splashMessage(msg)

    def message(self, caller, msg, details=''):
        """self.message(caller, str, str) -> str. Returns a string with a
        formatted message to be send to the debugging output. This
        should not be called explicitly from userland. Consider using
        self.log(), self.warning() or self.critical() instead."""
        msg = (msg + '\n' + details) if details else msg
        source = inspect.getsourcefile(caller)
        line = caller.f_lineno
        if source and line:
            return source + ", line " + str(line) + "\n" + msg
        else:
            return "(File info not available)\n" + msg

    def debug(self, msg, details = ''):
        """self.log(str, str) -> None. Send information message (low
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.debug(self.message(caller, msg, details))

    def log(self, msg, details = ''):
        """self.log(str, str) -> None. Send information message (low
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.info(self.message(caller, msg, details))

    def warning(self, msg, details = ''):
        """self.warning(str, str) -> None. Send warning message (medium
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.warning(self.message(caller, msg, details))

    def critical(self, msg, details = ''):
        """self.critical(str, str) -> None. Send critical message (high
        importance) to log with appropriate call site information."""
        caller = inspect.currentframe().f_back # who called us?
        self.logger.critical(self.message(caller, msg, details))

splashMessage = DebugPrint.getInstance().splashMessage
critical = DebugPrint.getInstance().critical
warning  = DebugPrint.getInstance().warning
log      = DebugPrint.getInstance().log
debug    = DebugPrint.getInstance().debug

#   critical: terminal, messagebox
#   warning: terminal
#   log : shown if -V 1
#   debug : shown if -V 2

################################################################################

def timecall(method):
    """timecall is a method decorator that wraps any call in timing calls
    so we get the total time taken by a function call as a debugging message."""
    def call(self, *args, **kwargs):
        caller = inspect.currentframe().f_back
        start = time.time()
        method(self, *args, **kwargs)
        end = time.time()
        critical("time: %.5s" % (end-start))
    call.__doc__ = method.__doc__
    return call

################################################################################

def object_at(desc):
    """object_at(id) -> object

    id is an int returning from id() or a hex string of id()

    Fetches all live objects, finds the one with given id, and returns
    it.  Warning: THIS IS FOR DEBUGGING ONLY. IT IS SLOW."""
    if isinstance(desc, int):
        target_id = desc
    elif isinstance(desc, basestring):
        target_id = int(desc, 16) # Reads desc as the hex address
    import gc
    for obj in gc.get_objects():
        if id(obj) == target_id:
            return obj
    raise KeyError("Couldn't find object")
