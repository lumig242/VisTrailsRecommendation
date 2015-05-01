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
from vistrails.db.domain import DBActionAnnotation

import unittest
import copy
import vistrails.core

class ActionAnnotation(DBActionAnnotation):

    ##########################################################################
    # Constructors and copy

    def __init__(self, *args, **kwargs):
        DBActionAnnotation.__init__(self, *args, **kwargs)
        if self.id is None:
            self.id = -1
        
    def __copy__(self):
        return ActionAnnotation.do_copy(self)

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBActionAnnotation.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = ActionAnnotation
        return cp

    @staticmethod
    def convert(_annotation):
        _annotation.__class__ = ActionAnnotation

    ##########################################################################
    # Properties

    id = DBActionAnnotation.db_id
    key = DBActionAnnotation.db_key
    value = DBActionAnnotation.db_value
    action_id = DBActionAnnotation.db_action_id
    date = DBActionAnnotation.db_date
    user = DBActionAnnotation.db_user

    ##########################################################################
    # Operators
    
    def __str__(self):
        """__str__() -> str - Returns a string representation of an
        ActionAnnotation object.

        """
        rep = ("<actionAnnotation id=%s action_id=%s key=%s value=%s "
               "date=%s user=%s</annotation>")
        return  rep % (str(self.id), str(self.action_id), str(self.key), 
                       str(self.value), str(self.date), str(self.user))

    def __eq__(self, other):
        """ __eq__(other: ActionAnnotation) -> boolean
        Returns True if self and other have the same attributes. Used by == 
        operator. 
        
        """
        if type(self) != type(other):
            return False
        if self.key != other.key:
            return False
        if self.value != other.value:
            return False
        if self.action_id != other.action_id:
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

################################################################################
# Unit tests


class TestActionAnnotation(unittest.TestCase):

    def create_annotation(self, id_scope=None):
        from vistrails.db.domain import IdScope

        if id_scope is None:
            id_scope = IdScope()
        annotation = \
            ActionAnnotation(id=id_scope.getNewId(ActionAnnotation.vtType),
                             key='akey', action_id=1L,
                             value='some value', user='test')
        return annotation

    def test_copy(self):
        from vistrails.db.domain import IdScope
        id_scope = IdScope()

        a1 = self.create_annotation(id_scope)
        a2 = copy.copy(a1)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)
        a3 = a1.do_copy(True, id_scope, {})
        self.assertEquals(a1, a3)
        self.assertNotEquals(a1.id, a3.id)

    def test_serialization(self):
        import vistrails.core.db.io
        a1 = self.create_annotation()
        xml_str = vistrails.core.db.io.serialize(a1)
        a2 = vistrails.core.db.io.unserialize(xml_str, ActionAnnotation)
        self.assertEquals(a1, a2)
        self.assertEquals(a1.id, a2.id)

    def test_str(self):
        a1 = self.create_annotation()
        str(a1)
