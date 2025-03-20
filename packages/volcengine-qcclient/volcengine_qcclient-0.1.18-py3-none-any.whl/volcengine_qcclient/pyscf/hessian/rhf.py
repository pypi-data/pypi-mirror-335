# Copyright (2025) Beijing Volcano Engine Technology Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from .._future import Future, create_methods_config, from_pyscf_instance
from ..scf import load_or_run_scf

class Hessian(Future):
    _keys = {'grids', 'grid_response', 'base'}
    _methods = ['.Hessian']
    _return = {
        'hess.de': 'de'
    }

    def __init__(self, mf):
        if not isinstance(mf, Future):
            mf = from_pyscf_instance(mf)
        self.base = mf
        self._job_client = mf._job_client
        self._task_config = []
        self._task_id = None

    def _build_task_config(self, with_return=True):
        task_config = load_or_run_scf(self.base)
        task_config.extend(create_methods_config(self, with_return))
        return task_config

    def synchronize(self):
        raise NotImplementedError

    def to_cpu(self):
        raise NotImplementedError
