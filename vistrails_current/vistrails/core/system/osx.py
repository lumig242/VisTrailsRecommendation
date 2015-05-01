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
""" Mac OS X specific file """
      
# from xml import dom
# from xml.dom.xmlbuilder import DOMInputSource, DOMBuilder
import xml.etree.cElementTree as ElementTree
import datetime
import os
import shutil
import subprocess
import time
from vistrails.core.system.unix import executable_is_in_path, list2cmdline, \
     executable_is_in_pythonpath, execute_cmdline, execute_piped_cmdlines
import vistrails.core.utils

import unittest

###############################################################################
# Extract system detailed information of a Mac system
#
# Based on a Python Cookbook recipe available online :
#    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/303063
# and in the Python Coobook, page 418
# Credit: Brian Quinlan
#
# Rewritten to use ElementTree instead of PyXML
#
# This recipe uses the system_profiler application to retrieve detailed
# information about a Mac OS X system. There are two useful ways to use it:
# the first is to ask for a complete Python datastructure containing
# information about the system (see OSXSystemProfiler.all()) and the 
# other is two ask for particular keys in the system information database.

def group(lst, n):
    """group([0,3,4,10,2,3], 2) => [(0,3), (4,10), (2,3)]
    
    Group a list into consecutive n-tuples. Incomplete tuples are
    discarded e.g.
    
    >>> group(range(10), 3)
    [(0, 1, 2), (3, 4, 5), (6, 7, 8)]
    
    """
    return zip(*[lst[i::n] for i in xrange(n)]) 

class OSXSystemProfiler(object):
    "Provide information from the Mac OS X System Profiler"

    def __init__(self, category=None, detail=None):
        """detail can range from -2 to +1, with larger numbers returning more
        information. Beware of +1, it can take several minutes for
        system_profiler to generate the data."""

        command = ['system_profiler', '-xml']
        if category is not None:
            command.append(str(category))
        if detail is not None:
            command.extend(['-detailLevel', '%d' % detail])
        p = subprocess.Popen(command, stdout=subprocess.PIPE)
        self.document = ElementTree.parse(p.stdout)

    def _content(self, node):
        "Get the text node content of an element or an empty string"
        return (node.text or '')

    def _convert_value_node(self, node):
        """Convert a 'value' node (i.e. anything but 'key') into a Python data
        structure"""
        if node.tag == 'string':
            return self._content(node)
        elif node.tag == 'integer':
            return int(self._content(node))
        elif node.tag == 'real':
            return float(self._content(node))
        elif node.tag == 'date': #  <date>2004-07-05T13:29:29Z</date>
            return datetime.datetime(
                *time.strptime(self._content(node), '%Y-%m-%dT%H:%M:%SZ')[:5])
        elif node.tag == 'array':
            return [self._convert_value_node(n) for n in node.getchildren()]
        elif node.tag == 'dict':
            return dict([(self._content(n), self._convert_value_node(m))
                for n, m in group(node.getchildren(), 2)])
        else:
            raise ValueError(node.tag)
    
    def __getitem__(self, key):
        nodes = self.document.getiterator('dict')
        results = []
        for node in nodes:
            for child in node:
                if child.tag == 'key' and child.text == key:
                    v = self._convert_value_node(node)[key]
                    if isinstance(v, dict) and v.has_key('_order'):
                        # this is just information for display
                        pass
                    else:
                        results.append(v)
        return results
    
#     def all(self):
#         """Return the complete information from the system profiler
#         as a Python data structure"""
        
#         return self._convert_value_node(
#             self.document.documentElement.firstChild)

###############################################################################

def example():
    from optparse import OptionParser
    from pprint import pprint

    info = OSXSystemProfiler("SPHardwareDataType")
    parser = OptionParser()
    parser.add_option("-f", "--field", action="store", dest="field",
                      help="display the value of the specified field")
    
    (options, args) = parser.parse_args()
    if len(args) != 0:
        parser.error("no arguments are allowed")
    
    if options.field is not None:
        pprint(info[options.field])
    else:
        # just print some comment keys known to exist in only one important
        # dictionary
        for k in ['cpu_type', 'current_processor_speed', 'l2_cache_size',
                  'physical_memory', 'user_name', 'os_version', 'ip_address']:
            print '%s: %s' % (k, info[k][0])

###############################################################################

def parse_meminfo():
    """ parse_meminfo() -> int
    Uses the system_profiler application to retrieve detailed information
    about a Mac OS X system. Returns memory size in Megabytes.
    
    Just use the "SPHardwareDataType" category to limit the amount of
    information gathered.

    """
        
    result = -1
    info = OSXSystemProfiler("SPHardwareDataType")
    mem = info['physical_memory'][0]
    # print "*** MEMORY", mem
    if mem.upper().endswith(' GB'):
        result = int(float(mem[:-3]) * 1024) * 1L
    elif mem.upper().endswidth(' MB'):
        result = int(mem[:-3]) * 1L
    # print '>>>>', result
    return result

def guess_total_memory():
    """ guess_total_memory() -> int 
    Return system memory in bytes. If PyXML is not installed it returns -1 
    
    """
    return parse_meminfo()

def temporary_directory():
    """ temporary_directory() -> str 
    Returns the path to the system's temporary directory 
    
    """
    return "/tmp/"

def home_directory():
    """ home_directory() -> str 
    Returns user's home directory using environment variable $HOME
    
    """
    return os.getenv('HOME')

def remote_copy_program():
    return "scp -p"

def remote_shell_program():
    return "ssh -p"

def graph_viz_dot_command_line():
    """ graph_viz_dot_command_line() -> str
    Returns dot command line

    """
    return 'dot -Tplain -o '

def remove_graph_viz_temporaries():
    """ remove_graph_viz_temporaries() -> None 
    Removes temporary files generated by dot 
    
    """
    os.unlink(temporary_directory() + "dot_output_vistrails.txt")
    os.unlink(temporary_directory() + "dot_tmp_vistrails.txt")

def link_or_copy(src, dst):
    """link_or_copy(src:str, dst:str) -> None 
    Tries to create a hard link to a file. If it is not possible, it will
    copy file src to dst 
    
    """
    # Links if possible, but we're across devices, we need to copy.
    try:
        os.link(src, dst)
    except OSError, e:
        if e.errno == 18:
            # Across-device linking is not possible. Let's copy.
            shutil.copyfile(src, dst)
        else:
            raise e

def get_executable_path(executable_name):
    vt_path = os.getenv("EXECUTABLEPATH")
    if vt_path is not None:
        vt_path = vt_path.strip()
        executable_path = \
            os.path.join(os.path.dirname(vt_path), executable_name)
        if os.path.exists(executable_path):
            return executable_path
    paths = os.environ['PATH']
    paths = paths.split(os.pathsep)
    for prefix in paths:
        path = os.path.join(prefix, executable_name)
        if os.path.exists(path):
            return path
    return None

################################################################################


class TestMacOSX(unittest.TestCase):
     """ Class to test Mac OS X specific functions """
     
     def test1(self):
         """ Test if guess_total_memory() is returning an int >= 0"""
         result = guess_total_memory()
         assert isinstance(result, (int, long))
         assert result >= 0

     def test2(self):
         """ Test if home_directory is not empty """
         result = home_directory()
         assert result != ""

     def test3(self):
         """ Test if temporary_directory is not empty """
         result = temporary_directory()
         assert result != ""

     def test_executable_file_in_path(self):
         # Should exist in any POSIX shell, which is what we have in OSX
         result = executable_is_in_path('ls')
         assert result == "/bin/ls" # Any UNIX should respect this.

if __name__ == '__main__':
    unittest.main()
             
