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

from .._future import Future, create_methods_config, Mole_to_task

class SCF(Future):
    _keys = {
        'conv_tol', 'conv_tol_grad', 'conv_tol_cpscf', 'max_cycle', 'init_guess',
        'level_shift', 'direct_scf_tol', 'disp',
    }

    _methods = []
    _return = {
        'scf.converged': 'converged',
        'scf.e_tot': 'e_tot',
        #'scf.mo_energy': 'mo_energy',
    }

    def __init__(self, mol):
        Future.__init__(self)
        self.mol = mol

    def _build_task_config(self, with_return=True):
        task_config = create_methods_config(self, with_return)
        task_config = [
            Mole_to_task(self.mol),
            *task_config,
            # TODO: use pyscf chkfile to serialize the SCF results
            # {'method':, 'dump_chk', 'kwargs': self._task_id + '.chk'},
        ]
        return task_config

    def kernel(self):
        self.run()
    scf = kernel

    def synchronize(self):
        raise NotImplementedError

    def density_fit(self, auxbasis=None):
        from volcengine_qcclient.pyscf.df import density_fit
        return density_fit(self, auxbasis)

    def newton(self):
        from volcengine_qcclient.pyscf.soscf import newton
        return newton(self)

    def x2c(self):
        from volcengine_qcclient.pyscf.x2c import x2c
        return x2c(self)

    def Gradients(self):
        from volcengine_qcclient.pyscf.grad.rhf import Gradients
        return Gradients(self)

    def nuc_grad_method(self):
        return self.Gradients()

    def Hessian(self):
        from volcengine_qcclient.pyscf.hessian.rhf import Hessian
        return Hessian(self)

    def TDA(self):
        from volcengine_qcclient.pyscf.tdscf import TDA
        return TDA(self)

    def TDDFT(self):
        from volcengine_qcclient.pyscf.tdscf import TDDFT
        return TDDFT(self)

    def PCM(self):
        from volcengine_qcclient.pyscf.solvent.pcm import pcm_for_scf
        return pcm_for_scf(self)

    def SMD(self):
        from volcengine_qcclient.pyscf.solvent.smd import smd_for_scf
        return smd_for_scf(self)

class RHF(SCF):
    _methods = ['gpu4pyscf.scf.RHF']

