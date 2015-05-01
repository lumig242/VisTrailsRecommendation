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

import uuid
from datetime import date, datetime
from time import strptime
################################################################################                           

def conv_to_bool(x):
    if isinstance(x, str):
        s = str(x).upper()
        if s == 'TRUE':
            return True
        if s == 'FALSE':
            return False
    elif isinstance(x, (int, long)):
        if x == 0:
            return False
        else:
            return True
    elif isinstance(x, bool):
        return x
        
def conv_from_bool(x):
    if isinstance(x, bool):
        if x == True:
            return 1
        else:
            return 0
    elif isinstance(x, (int, long)):
        return x
    
def convert_symbols(val):
    val = val.replace("&lt;", "<")
    val = val.replace("&gt;", ">")
    val = val.replace("&amp;","&")
    return val



#class XMLObject(object):
#    """Base class for mashup classes"""
#    @staticmethod
#    def convert_from_str(value, type):
#        def bool_conv(x):
#            s = str(x).upper()
#            if s == 'TRUE':
#                return True
#            if s == 'FALSE':
#                return False
#
#        if value is not None:
#            if type == 'str':
#                return str(value)
#            elif value.strip() != '':
#                if type == 'long':
#                    return long(value)
#                elif type == 'float':
#                    return float(value)
#                elif type == 'int':
#                    return int(value)
#                elif type == 'bool':
#                    return bool_conv(value)
#                elif type == 'date':
#                    return date(*strptime(value, '%Y-%m-%d')[0:3])
#                elif type == 'datetime':
#                    return datetime(*strptime(value, '%Y-%m-%d %H:%M:%S')[0:6])
#                elif type == 'uuid':
#                    return uuid.UUID(value)
#        return None
#
#    @staticmethod
#    def convert_to_str(value,type):
#        if value is not None:
#            if type == 'date':
#                return value.isoformat()
#            elif type == 'datetime':
#                return value.strftime('%Y-%m-%d %H:%M:%S')
#            else:
#                return str(value)
#        return ''
#    
#    @staticmethod
#    def indent(elem, level=0):
#        i = "\n" + level*"  "
#        if len(elem):
#            if not elem.text or not elem.text.strip():
#                elem.text = i + "  "
#            if not elem.tail or not elem.tail.strip():
#                elem.tail = i
#            for elem in elem:
#                XMLObject.indent(elem, level+1)
#            if not elem.tail or not elem.tail.strip():
#                elem.tail = i
#        else:
#            if level and (not elem.tail or not elem.tail.strip()):
#                elem.tail = i
################################################################################