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

import os
from typing import List, Dict, Union
from functools import lru_cache
from importlib import import_module
import json
import tempfile
import requests
import h5py
from volcengine_qcclient import QcService, QcBatchJob
from volcengine_qcclient.qc_batchjob import _generate_label

#TODO: load configurations like ak, sk, resource requirements, timeout, etc.
# from rc files or environments
ak = None
sk = None
QC_SERVICE_ID = os.environ.get('QC_SERVICE_ID')

@lru_cache(100)
class _QcPySCFRPCJob(QcBatchJob):

    def __init__(self, ak: str = None, sk: str = None,
                 qc_service_id: str = None,
                 label: str = None):
        super().__init__(ak, sk, qc_service_id, label)

    # submit qc tasks to server.
    def submit(self, task_config: Union[Dict, List[Dict]], dryrun=False) -> List[str]:
        assert task_config
        params = {
            "QcServiceId": self.qc_service_id,
            "TaskType": 'pyscf-rpc',
            "Label": self.label,
            "QcTasks": [{
                "MoleculeXyzData": 'YQ==',
                "MoleculeName": 'a',
                'QcTaskConfig': {'tasks': task_config}
            }],
        }
        if dryrun:
            params['QcTasks'][0]['QcTaskConfig']['dryrun'] = True

        try:
            data = self.qc_service.submit_qc_tasks(params=params)
        except TypeError:
            for method in task_config.items():
                for key, val in method.get('kwargs', {}).items():
                    try:
                        json.dumps(val)
                    except TypeError:
                        print(f'Kwarg {key} for {method} not JSON serializable: {val}')
                for key, val in method.get('attributes', {}).items():
                    try:
                        json.dumps(val)
                    except TypeError:
                        print(f'Attribute {key} for {method} not JSON serializable: {val}')
            raise InputError('Inputs not JSON serializable')
        except Exception:
            print(params)
            raise

        task_ids = data["Ids"]
        return task_ids

class Future:
    dryrun = False
    _timeout = None
    _methods = []
    _return = {} # Return in HDF5 output

    def __init__(self):
        self._job_client = _QcPySCFRPCJob(ak, sk, QC_SERVICE_ID)
        self._task_id = None

    def _build_task_config(self, with_return=True):
        raise NotImplementedError

    def _unpack_return(self, task=None):
        if self._task_id is None:
            raise RuntimeError('Job not submitted')

        if task is None:
            task = self._job_client.get_tasks([self._task_id])[0]
        url = task['OutputUrl']
        with tempfile.NamedTemporaryFile(suffix='.h5') as tmpf:
            filename = tmpf.name
            with open(filename, 'wb') as f:
                f.write(requests.get(url).content)
            with h5py.File(filename, 'r') as ret:
                for key, attr in self._return.items():
                    if key in ret:
                        _nested_set(self, attr, ret[key][()])
        return self

    def set(self, **kwargs):
        self.__dict__.update(kwargs)
        return self

    def run(self, **kwargs):
        self.__dict__.update(kwargs)
        task_config = self._build_task_config()
        task_ids = self._job_client.submit(task_config, self.dryrun)
        self._task_id = task_ids[0]
        self._job_client.wait(self._timeout)

        # TODO: handle errors raised remotely
        task = self._job_client.get_tasks([self._task_id])[0]
        response = requests.get(task['LogUrl'])
        log = response.text
        print(log)
        if task['Status'] == 'Failed':
            raise RPCServerError
        if not self.dryrun:
            self._unpack_return(task)
        return self

    def to_cpu(self):
        '''Convert to the corresponding PySCF instance'''
        if self._task_id is not None:
            self.synchronize()
        return to_cpu(self)

    def synchronize(self):
        raise NotImplementedError

    def done(self):
        if self._task_id is None:
            return False

        summary = self._job_client.get_task_summary()
        is_finished = True
        for status in ["Running", "Pending", "Killed"]:
            if status in summary and summary[status] > 0:
                is_finished = False
                break
        return is_finished

    def exception(self):
        raise NotImplementedError

    def cancel(self):
        if self._task_id is not None:
            self._job_client.stop()
        return True

class SubOptions:
    _keys = set()
    _return = {}

def extract_keys(cls):
    cls_keys = [c._keys for c in cls.__mro__[:-1] if hasattr(c, '_keys')]
    if len(cls_keys) == 1:
        return cls_keys[0]
    else:
        return cls_keys[0].union(*cls_keys[1:])

def to_cpu(method, out=None):
    if out is None:
        from pyscf.lib.misc import omniobj
        mod_path = method.__module__.split('.', 1)[1]
        mod = import_module(mod_path)
        cls = getattr(mod, method.__class__.__name__)

        # A temporary CPU instance. This ensures to initialize private
        # attributes that are only available for CPU code.
        out = cls(omniobj)

    # Convert only the keys that are defined in the corresponding CPU class
    cls_keys = extract_keys(out.__class__)
    out_keys = set(out.__dict__).union(cls_keys)
    # Only overwrite the attributes of the same name.
    keys = set(method.__dict__).intersection(out_keys)
    for key in keys:
        val = getattr(method, key)
        if hasattr(val, 'to_cpu'):
            val = val.to_cpu()
        setattr(out, key, val)
    return out

def Mole_to_task(mol):
    '''Convert pyscf.gto.Mole object into a task that can be recreated remotely'''
    if isinstance(mol, SubOptions):
        return mol._build_task_config()
    else:
        return {
            'method': 'pyscf.gto.mole.loads',
            'kwargs': {'molstr': mol.dumps()}
        }

def from_pyscf_instance(obj):
    from pyscf.lib import StreamObject
    assert isinstance(obj, StreamObject)

    # guess the class
    mod_name = obj.__class__.__module__
    klass = obj.__class__.__name__

    # load the klass
    mod = import_module(f'volcengine_qcclient.{mod_name}')
    klass = getattr(mod, klass)
    return klass(obj.mol)

def check_attributes(obj):
    attrs = obj.__dict__
    supported_keys = extract_keys(obj.__class__)
    _keys = supported_keys.intersection(attrs)

    remained_keys = set(attrs).difference(_keys)
    # Some attributes are created by almost every class
    remained_keys.difference_update(
        {'dryrun', 'mol', 'cell', 'max_memory', 'base'}
    )
    # Some attributes are set by "return" from previous jobs
    if hasattr(obj, '_return'):
        remained_keys.difference_update(obj._return.values())
    # Exclude _task_id, _job_client, etc.
    unknown = [k for k in remained_keys if k[0] != '_']
    if unknown:
        print(f'Unsupported attributes {unknown}')

    # Handle the nested attrs, such as with_df, with_solvent
    out = {}
    for key in _keys:
        attr = attrs[key]
        if isinstance(attr, SubOptions):
            sub_attrs = check_attributes(attr)
            for sub_key, sub_val in sub_attrs.items():
                out[key + '.' + sub_key] = sub_val
        elif not isinstance(attr, Future):
            # Avoid assigning attributes recursively.
            # Typically, create_methods_config for sub-Future attributes is
            # called explictly for methods like tddft._scf, Gradients.base.
            # Attributes can be properly assigned there.
            out[key] = attr
    return out

def create_methods_config(obj, with_return=True):
    '''Construct a configuration representing the process of instantiating a
    PySCF class. If with_return is disabled, this configuration only builds the
    instance. The .run() method of the instance will not be executed.
    '''
    assert len(obj._methods) > 0
    task_config = [{'method': method} for method in obj._methods]

    last_task = task_config[-1]
    attrs = check_attributes(obj)
    if attrs:
        last_task['attributes'] = attrs

    if with_return:
        last_task['return'] = obj._return
    return task_config

def _nested_get(obj, key):
    if '.' in key:
        # key is a nested attribute
        val = obj
        for k in key.split('.'):
            val = getattr(val, k)
    else:
        val = getattr(obj, key)
    return val

def _nested_set(obj, key, val):
    if '.' in key:
        keys = key.split('.')
        for k in keys[:-1]:
            obj = getattr(obj, k)
        setattr(obj, keys[-1], val)
    else:
        setattr(obj, key, val)

class RPCServerError(RuntimeError):
    pass

class InputError(RuntimeError):
    pass
