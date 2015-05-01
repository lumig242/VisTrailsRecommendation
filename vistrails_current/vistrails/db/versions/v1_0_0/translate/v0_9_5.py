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
import copy
from vistrails.db.versions.v1_0_0.domain import DBVistrail, DBWorkflow, DBLog, \
    DBRegistry, DBModuleExec, DBGroupExec, DBLoopExec, DBGroup

def translateVistrail(_vistrail):
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBGroup': {'workflow': update_workflow}}
    vistrail = DBVistrail.update_version(_vistrail, translate_dict)
    vistrail.db_version = '1.0.0'
    return vistrail

def translateWorkflow(_workflow):
    def update_workflow(old_obj, translate_dict):
        return DBWorkflow.update_version(old_obj.db_workflow, translate_dict)
    translate_dict = {'DBGroup': {'workflow': update_workflow}}
    workflow = DBWorkflow.update_version(_workflow, translate_dict)
    workflow.db_version = '1.0.0'
    return workflow

def translateLog(_log):
    def update_item_execs(old_obj, translate_dict):
        new_item_execs = []
        for obj in old_obj.db_items:
            if obj.vtType == 'module_exec':
                new_item_execs.append(DBModuleExec.update_version(obj, translate_dict))
            elif obj.vtType == 'group_exec':
                new_item_execs.append(DBGroupExec.update_version(obj, translate_dict))
            elif obj.vtType == 'loop_exec':
                new_item_execs.append(DBLoopExec.update_version(obj, translate_dict))
        return new_item_execs

    def update_sub_item_execs(old_obj, translate_dict, do_loop_execs=True):
        new_item_execs = []
        for obj in old_obj.db_module_execs:
            new_item_execs.append(DBModuleExec.update_version(obj, translate_dict))
        for obj in old_obj.db_group_execs:
            new_item_execs.append(DBGroupExec.update_version(obj, translate_dict))
        if do_loop_execs:
            for obj in old_obj.db_loop_execs:
                new_item_execs.append(DBLoopExec.update_version(obj, translate_dict))
        return new_item_execs

    def update_group_item_execs(old_obj, translate_dict):
        return update_sub_item_execs(old_obj, translate_dict)

    def update_loop_item_execs(old_obj, translate_dict):
        return update_sub_item_execs(old_obj, translate_dict, False)

    translate_dict = {'DBWorkflowExec': {'item_execs': update_item_execs},
                      'DBGroupExec': {'item_execs': update_group_item_execs},
                      'DBLoopExec': {'item_execs': update_loop_item_execs}}
    log = DBLog.update_version(_log, translate_dict)
    log.db_version = '1.0.0'
    return log

def translateRegistry(_registry):
    translate_dict = {}
    registry = DBRegistry.update_version(_registry, translate_dict)
    registry.db_version = '1.0.0'
    return registry
