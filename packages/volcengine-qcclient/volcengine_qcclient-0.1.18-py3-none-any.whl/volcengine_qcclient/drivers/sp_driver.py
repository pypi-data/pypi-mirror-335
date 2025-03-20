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
import time
import json
import pyscf
import cupy
import traceback
import h5py

from pyscf import lib, gto
from pyscf import dft, scf
from pyscf.hessian import thermo
from pyscf.lib import logger

default_config = {
    'input_dir': './',
    'output_dir': './',
    'molecule': 'molecule.xyz',
    'threads': 8,
    'max_memory': 32000,

    'charge': 0,
    'spin': None,
    'xc': 'b3lyp',
    'disp': None,
    'grids': {'atom_grid': (99,590)},
    'nlcgrids': {'atom_grid': (50,194)},
    'basis': 'def2-tzvpp',
    'verbose': 4,
    'scf_conv_tol': 1e-10,
    'direct_scf_tol': 1e-14,
    'with_df': True,
    'auxbasis': None,
    'with_gpu': True,

    'with_grad': True,
    'with_hess': True,
    'with_thermo': False,
    'save_density': False,

    'with_dm': True,
    'with_chelpg': False,
    'with_dipole': False,

    'with_solvent': False,
    'solvent': {'method': 'iefpcm', 'eps': 78.3553, 'solvent': 'water'},
}

def run_dft(config):
    ''' Perform DFT calculations based on the configuration file.
    Saving the results, timing, and log to a HDF5 file.
    '''
    config = {**default_config, **config}

    mol_name = config['molecule']
    assert isinstance(mol_name, str)
    assert mol_name.endswith('.xyz')
    input_dir = config['input_dir']
    output_dir = config['output_dir']
    if not os.path.exists(f'{input_dir}/{mol_name}'):
        raise RuntimeError(f'Input file {input_dir}/{mol_name} does not exist.')

    # I/O
    logfile = mol_name[:-4] + '_pyscf.log'
    data_file = mol_name[:-4] + '_pyscf.h5'
    os.makedirs(output_dir, exist_ok=True)

    lib.num_threads(config['threads'])
    start_time = time.time()
    mol = pyscf.M(
        atom=f'{input_dir}/{mol_name}',
        basis=config['basis'],
        max_memory=float(config['max_memory']),
        verbose=config['verbose'],
        charge=config['charge'],
        spin=config['spin'],
        output=f'{output_dir}/{logfile}')

    # To match default LDA in Q-Chem
    xc = config['xc']
    if xc == 'LDA':
        xc = 'LDA,VWN5'

    if xc.lower() == 'hf':
        mf = scf.HF(mol)
    else:
        mf = dft.KS(mol, xc=xc)
        grids = config['grids']
        nlcgrids = config['nlcgrids']
        if 'atom_grid' in grids: mf.grids.atom_grid = grids['atom_grid']
        if 'level' in grids:     mf.grids.level     = grids['level']
        if mf._numint.libxc.is_nlc(mf.xc):
            if 'atom_grid' in nlcgrids: mf.nlcgrids.atom_grid = nlcgrids['atom_grid']
            if 'level' in nlcgrids:     mf.nlcgrids.level     = nlcgrids['level']
    mf.disp = config['disp']
    if config['with_df']:
        auxbasis = config['auxbasis']
        if auxbasis == "RIJK-def2-tzvp":
            auxbasis = 'def2-tzvp-jkfit'
        mf = mf.density_fit(auxbasis=auxbasis)

    if config['with_gpu']:
        cupy.get_default_memory_pool().free_all_blocks()
        mf = mf.to_gpu()

    mf.chkfile = None
    if config['with_solvent']:
        solvent = config['solvent']
        # TODO: check whether solvent['solvent'] and solvent['eps'] are absent.
        # If both are specified, test whether they are conflicted.
        # If only one of them is specified, create the other one from database
        # if necessary.
        if solvent['method'].endswith(('PCM', 'pcm')):
            mf = mf.PCM()
            mf.with_solvent.lebedev_order = 29
            mf.with_solvent.method = solvent['method'].replace('PCM','-PCM')
            mf.with_solvent.eps = solvent['eps']
        elif solvent['method'].endswith(('smd', 'SMD')):
            mf = mf.SMD()
            mf.with_solvent.lebedev_order = 29
            mf.with_solvent.method = 'SMD'
            mf.with_solvent.solvent = solvent['solvent']
        else:
            raise NotImplementedError

    mf.direct_scf_tol = config['direct_scf_tol']
    mf.chkfile = None
    mf.conv_tol = float(config['scf_conv_tol'])
    e_tot = mf.kernel()

    if not mf.converged:
        logger.warn(mf, 'SCF failed to converge')

    scf_time = time.time() - start_time
    print(f'compute time for energy: {scf_time:.3f} s')

    e1        = mf.scf_summary.get('e1',         0.0)
    e_coul    = mf.scf_summary.get('coul',       0.0)
    e_xc      = mf.scf_summary.get('exc',        0.0)
    e_disp    = mf.scf_summary.get('dispersion', 0.0)
    e_solvent = mf.scf_summary.get('e_solvent',  0.0)

    with h5py.File(f'{output_dir}/{data_file}', 'w') as h5f:
        h5f.create_dataset('e_tot',     data=e_tot)
        h5f.create_dataset('e1',        data=e1)
        h5f.create_dataset('e_coul',    data=e_coul)
        h5f.create_dataset('e_xc',      data=e_xc)
        h5f.create_dataset('e_disp',    data=e_disp)
        h5f.create_dataset('e_solvent', data=e_solvent)
        h5f.create_dataset('scf_time',  data=scf_time)

        dm = mf.make_rdm1()
        if config['with_dipole']:
            h5f['dipole'] = mf.dip_moment()
            h5f['quadrupole'] =  mf.quad_moment()

        if config['with_chelpg']:
            from gpu4pyscf.qmmm import chelpg
            q = chelpg.eval_chelpg_layer_gpu(mf)
            h5f['chelpg'] = ensure_nparray(q)
            q = None

        if config['with_dm']:
            h5f['dm'] = ensure_nparray(dm)

        if config['save_density'] and xc.lower() != 'hf':
            weights = mf.grids.weights
            coords = mf.grids.coords
            dm0 = dm[0] + dm[1] if dm.ndim == 3 else dm
            rho = mf._numint.get_rho(mf.mol, dm0, mf.grids)

            h5f['grids_weights'] = ensure_nparray(weights)
            h5f['grids_coords']  = ensure_nparray(coords)
            h5f['grids_rho']     = ensure_nparray(rho)
            weights = coords = dm0 = rho = None

        if dm.ndim == 3:
            # open-shell case
            mo_energy = ensure_nparray(mf.mo_energy).copy()
            mo_energy[0].sort()
            mo_energy[1].sort()
            na, nb = mf.nelec
            h5f.create_dataset('e_lumo_alpha',   data=mo_energy[0][na])
            h5f.create_dataset('e_lumo_beta',    data=mo_energy[1][nb])
            h5f.create_dataset('e_homo_alpha',   data=mo_energy[0][na-1])
            h5f.create_dataset('e_homo_beta',    data=mo_energy[1][nb-1])
        else:
            # closed-shell case
            mo_energy = ensure_nparray(mf.mo_energy).copy()
            mo_energy.sort()
            nocc = mf.mol.nelectron // 2
            h5f.create_dataset('e_lumo',     data=mo_energy[nocc])
            h5f.create_dataset('e_homo',     data=mo_energy[nocc-1])
        dm = None

    ##################### Gradient Calculation ###############################
    g = None
    if config['with_grad']:
        start_time = time.time()
        g = mf.nuc_grad_method()
        if config['with_df']:
            g.auxbasis_response = True
        f = g.kernel()
        g = None
        grad_time = time.time() - start_time
        print(f'compute time for gradient: {grad_time:.3f} s')

        with h5py.File(f'{output_dir}/{data_file}', 'a') as h5f:
            h5f.create_dataset('grad', data=f)
            h5f.create_dataset('grad_time', data=grad_time)

    #################### Hessian Calculation ###############################
    h = None
    if config['with_hess'] or config['with_thermo']:
        natm = mol.natm
        start_time = time.time()
        h = mf.Hessian()
        h.auxbasis_response = 2
        _h_dft = h.kernel()
        h_dft = _h_dft.transpose([0,2,1,3]).reshape([3*natm, 3*natm])
        hess_time = time.time() - start_time
        print(f'compute time for hessian: {hess_time:.3f} s')

        if config['with_thermo']:
            # harmonic analysis
            start_time = time.time()
            normal_mode = thermo.harmonic_analysis(mol, _h_dft)

            thermo_dat = thermo.thermo(
                mf,                            # GPU4PySCF object
                normal_mode['freq_au'],
                298.15,                            # room temperature
                101325)                            # standard atmosphere
            thermo_time = time.time() - start_time
            print(f'compute time for harmonic analysis: {thermo_time:.3f} s')

        with h5py.File(f'{output_dir}/{data_file}', 'a') as h5f:
            h5f.create_dataset('hess', data=h_dft)
            h5f.create_dataset('hess_time', data=hess_time)

            if config['with_thermo']:
                h5f.create_dataset('freq_au',         data=normal_mode['freq_au'])
                h5f.create_dataset('freq_wavenumber', data=normal_mode['freq_wavenumber'])
                h5f.create_dataset('E_tot',           data=thermo_dat['E_tot'][0])
                h5f.create_dataset('H_tot',           data=thermo_dat['H_tot'][0])
                h5f.create_dataset('G_tot',           data=thermo_dat['G_tot'][0])
                h5f.create_dataset('E_elec',          data=thermo_dat['E_elec'][0])
                h5f.create_dataset('E_trans',         data=thermo_dat['E_trans'][0])
                h5f.create_dataset('E_rot',           data=thermo_dat['E_rot'][0])
                h5f.create_dataset('E_vib',           data=thermo_dat['E_vib'][0])
                h5f.create_dataset('E_0K',            data=thermo_dat['E_0K'][0])
                h5f.create_dataset('H_elec',          data=thermo_dat['H_elec'][0])
                h5f.create_dataset('H_trans',         data=thermo_dat['H_trans'][0])
                h5f.create_dataset('H_rot',           data=thermo_dat['H_rot'][0])
                h5f.create_dataset('H_vib',           data=thermo_dat['H_vib'][0])
                h5f.create_dataset('G_elec',          data=thermo_dat['G_elec'][0])
                h5f.create_dataset('G_trans',         data=thermo_dat['G_trans'][0])
                h5f.create_dataset('G_rot',           data=thermo_dat['G_rot'][0])
                h5f.create_dataset('G_vib',           data=thermo_dat['G_vib'][0])
    return mf

def ensure_nparray(a):
    if isinstance(cupy.ndarray):
        a = a.get()
    return np.asarray(a)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Run DFT with GPU4PySCF for molecules')
    parser.add_argument(
        "config",
        type=str,
        help="Path to the configuration file (e.g., example.json)"
    )
    args = parser.parse_args()
    with open(args.config) as f:
        config = json.load(f)
        if isinstance(config, list):
            config = config[0]
    run_dft(config)
