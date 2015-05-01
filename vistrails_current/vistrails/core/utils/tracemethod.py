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
"""Defines a trace decorator that traces function calls. This is not currently
thread-safe. It won't crash, but the bump() printouts might not be correct.

Also defines report_stack, a decorator that dumps the traceback whenever
a method gets called."""
import sys
import traceback
from vistrails.core.data_structures.stack import Stack

import unittest
import tempfile
import os

_output_file = sys.stderr

__current_method_name = Stack()

def _indent():
    _output_file.write(' ' * (len(__current_method_name)-1))

def trace_method_options(method,
                         with_args=False,
                         with_kwargs=False,
                         with_return=False):
    """trace_method_options is a method decorator that traces
    entry-exit of functions. It also prints args, kwargs and return
    values if optional parameters with_args, with_kwargs and
    with_return are set to True."""
    def decorated(self, *args, **kwargs):
        __current_method_name.push([method.__name__, 0])
        try:
            _indent()
            _output_file.write(method.__name__ +  ".enter")
            if with_args:
                _output_file.write(" (args: ")
                _output_file.write(str([str(arg) for arg in args]))
                _output_file.write(")")
            if with_kwargs:
                _output_file.write(" (kwargs: ")
                kwarglist = [(k, str(v)) for (k,v) in kwargs.iteritems()]
                kwarglist.sort()
                _output_file.write(str(kwarglist))
                _output_file.write(")")
            _output_file.write('\n')
            result = method(self, *args, **kwargs)
            _indent()
            _output_file.write(method.__name__ + ".exit")
            if with_return:
                _output_file.write(" (return: %s)" % str(result))
            _output_file.write('\n')
        finally:
            __current_method_name.pop()
        return result
    return decorated

def trace_method(method):
    return trace_method_options(method)

def trace_method_args(method):
    return trace_method_options(method, with_args=True)

def bump_trace():
    __current_method_name.top()[1] += 1
    _indent()
    _output_file.write('%s.%s\n' % tuple(__current_method_name.top()))

def report_stack(method):
    def decorated(self, *args, **kwargs):
        print "-" * 78
        try:
            print "Method: " + method.im_class.__name__ + '.' + method.__name__
        except:
            pass
        try:
            print "Function: " + method.func_name
        except:
            pass
        traceback.print_stack()
        print "-" * 78
        return method(self, *args, **kwargs)
    return decorated
        
###############################################################################


@trace_method
def test_fun(p1):
    return p1 + 5

@trace_method
def test_fun_2(p1):
    bump_trace()
    result = test_fun(p1) + 3
    bump_trace()
    return result

class TestTraceMethod(unittest.TestCase):

    def test_trace_1(self):
        global _output_file
        (fd, name) = tempfile.mkstemp()
        os.close(fd)
        try:
            _output_file = open(name, 'w')

            x = test_fun(10)
            self.assertEquals(x, 15)

            _output_file.close()
            _output_file = sys.stderr

            output = "".join(open(name, 'r').readlines())
            self.assertEquals(output,
                              'test_fun.enter\n' +
                              'test_fun.exit\n')
        finally:
            os.unlink(name)

    def test_trace_2(self):
        global _output_file
        (fd, name) = tempfile.mkstemp()
        os.close(fd)
        _output_file = open(name, 'w')

        x = test_fun_2(10)
        self.assertEquals(x, 18)
        
        _output_file.close()
        _output_file = sys.stderr

        output = "".join(open(name, 'r').readlines())
        self.assertEquals(output,
                          'test_fun_2.enter\n' +
                          'test_fun_2.1\n' +
                          ' test_fun.enter\n' +
                          ' test_fun.exit\n' +
                          'test_fun_2.2\n' +
                          'test_fun_2.exit\n')
        os.unlink(name)

if __name__ == '__main__':
    unittest.main()
