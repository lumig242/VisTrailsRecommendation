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
from vistrails.core.log.module_exec import ModuleExec
from vistrails.core.log.loop_exec import LoopExec
from vistrails.core.vistrail.annotation import Annotation
from vistrails.db.domain import DBGroupExec

class GroupExec(DBGroupExec):
    """ Class that stores info for logging a group/abstraction execution. """

    def __init__(self, *args, **kwargs):
        DBGroupExec.__init__(self, *args, **kwargs)

    def __copy__(self):
        return self.do_copy()

    def do_copy(self, new_ids=False, id_scope=None, id_remap=None):
        cp = DBGroupExec.do_copy(self, new_ids, id_scope, id_remap)
        cp.__class__ = GroupExec
        return cp

    @staticmethod
    def convert(_group_exec):
        if _group_exec.__class__ == GroupExec:
            return
        _group_exec.__class__ = GroupExec
        for annotation in _group_exec.annotations:
            Annotation.convert(annotation)
        for item_exec in _group_exec.item_execs:
            if item_exec.vtType == ModuleExec.vtType:
                ModuleExec.convert(item_exec)
            elif item_exec.vtType == GroupExec.vtType:
                GroupExec.convert(item_exec)
            elif item_exec.vtType == LoopExec.vtType:
                LoopExec.convert(item_exec)            

    ##########################################################################
    # Properties

    id = DBGroupExec.db_id
    ts_start = DBGroupExec.db_ts_start
    ts_end = DBGroupExec.db_ts_end
    cached = DBGroupExec.db_cached
    module_id = DBGroupExec.db_module_id
    group_name = DBGroupExec.db_group_name
    group_type = DBGroupExec.db_group_type
    completed = DBGroupExec.db_completed
    error = DBGroupExec.db_error
    machine_id = DBGroupExec.db_machine_id

    def _get_duration(self):
        if self.db_ts_end is not None:
            return self.db_ts_end - self.db_ts_start
        return None
    duration = property(_get_duration)

    def _get_annotations(self):
        return self.db_annotations
    def _set_annotations(self, annotations):
        self.db_annotations = annotations
    annotations = property(_get_annotations, _set_annotations)
    def add_annotation(self, annotation):
        self.db_add_annotation(annotation)

    def _get_item_execs(self):
        return self.db_item_execs
    def _set_item_execs(self, item_execs):
        self.db_item_execs = item_execs
    item_execs = property(_get_item_execs, _set_item_execs)
    def add_item_exec(self, item_exec):
        self.db_add_item_exec(item_exec)

