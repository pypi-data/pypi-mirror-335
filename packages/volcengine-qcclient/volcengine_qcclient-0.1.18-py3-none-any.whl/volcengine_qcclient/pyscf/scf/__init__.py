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

from .hf import RHF
from .uhf import UHF

__all__ = [
    'RHF', 'UHF',
    'load_or_run_scf'
]

def load_or_run_scf(mf):
    from .._future import create_methods_config
    if mf._task_id is None: # SCF not executed
        task_config = mf._build_task_config()
    else:
        task_config = mf._build_task_config()
        #TODO: Recover from previous jobs
        #task_config = create_methods_config(mf, with_return=False)
        #task_config = [
        #    Mole_to_task(mf.mol),
        #    *task_config,
        #    # FIXME: deserialization remotely
        #    {'method': 'update_from_chk', 'kwargs': mf._task_id + '.chk'}
        #]
    return task_config
