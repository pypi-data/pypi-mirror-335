#****************************************************************************
#* task_ctor.py
#*
#* Copyright 2023-2025 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may 
#* not use this file except in compliance with the License.  
#* You may obtain a copy of the License at:
#*  
#*   http://www.apache.org/licenses/LICENSE-2.0
#*  
#* Unless required by applicable law or agreed to in writing, software 
#* distributed under the License is distributed on an "AS IS" BASIS, 
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
#* See the License for the specific language governing permissions and 
#* limitations under the License.
#*
#* Created on:
#*     Author: 
#*
#****************************************************************************
import os
import json
import dataclasses as dc
import logging
from pydantic import BaseModel
from typing import Any, Callable, ClassVar, Dict, List, Tuple
from .task_data import TaskDataOutput, TaskDataResult

# TaskParamsCtor accepts an evaluation context and returns a task parameter object
TaskParamsCtor = Callable[[object], Any]

@dc.dataclass
class TaskCtor(object):
    name : str
    uses : 'TaskCtor' = None
    srcdir : str = None

    _log : ClassVar = logging.getLogger("TaskCtor")

    def mkTask(self, name : str, srcdir=None) -> 'TaskNode':
        """Creates a task object"""
        if srcdir is None:
            srcdir = self.srcdir

        if self.uses is not None:
            return self.uses.mkTask(name, srcdir)
        else:
            raise NotImplementedError("TaskCtor.mkTask() not implemented for %s" % str(type(self)))
    
    def mkParams(self, params=None) -> TaskParamsCtor:
        """Creates a list of task-parameter objects used produce the params object"""
        self._log.debug("--> %s::mkParams" % self.name)
        if self.uses is not None:
            params = self.uses.mkParams()
        else:
            params = TaskParams()
        self._log.debug("<-- %s::mkParams: %s" % (self.name, str(params)))

        return params

    def applyParams(self, params):
        if self.uses is not None:
            self.uses.applyParams(params)
