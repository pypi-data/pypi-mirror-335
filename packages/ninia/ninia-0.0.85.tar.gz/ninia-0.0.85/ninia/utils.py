
from fnmatch import filter as flt  # Native filter() function is used as well
from typing import Type, Union, List, Tuple
from dataclasses import dataclass
import pkg_resources
import sys
import os
import re

from ase import Atom, Atoms
import pandas as pd
import numpy as np

# Pull in molar mass data from separate csv file
mm_data = pkg_resources.resource_stream(__name__, 'data/mm_of_elements.csv')
molarmass_df = pd.read_csv(mm_data, encoding=sys.stdout.encoding, index_col=0)
# TODO - see if we can pull this in relatively with just pandas - I don't remember


@dataclass
class Control:
    calculation: str = 'relax'
    prefix: str = 'untitled'
    outdir: str = None
    pseudo_dir: str = None
    nstep: int = None
    verbosity: str = None
    restart_mode: str = None
    dt: float = None
    max_seconds: float = None
    forc_conv_thr: float = None
    etot_conv_thr: float = None
    lelfield: Union[bool, str] = None
    dipfield: Union[bool, str] = None
    tefield: Union[bool, str] = None


@dataclass
class System:
    ibrav: int = 0
    celldm: List[float] = None
    A: float = None
    B: float = None
    C: float = None
    cosAB: float = None
    cosAC: float = None
    cosBC: float = None
    nat: int = None
    ntyp: int = None
    nbnd: int = None
    tot_charge: float = None
    ecutwfc: float = None
    ecutrho: float = None
    nosym: Union[bool, str] = None
    nosym_evc: Union[bool, str] = None
    occupations: str = 'smearing'
    degauss: float = 0.02
    smearing: str = 'mv'
    nspin: int = None
    input_dft: str = None
    assume_isolated: str = None
    esm_bc: str = None
    starting_magnetizations: List[int] = None
    noncolin: Union[bool, str] = None
    edir: int = None
    emaxpos: float = None
    eopreg: float = None
    eamp: float = None


@dataclass
class Electrons:
    electron_maxstep: int = None
    scf_must_converge: Union[bool, str] = None
    conv_thr: float = None
    adaptive_thr: Union[bool, str] = None
    conv_thr_init: float = None
    mixing_mode: str = None
    mixing_beta: float = 0.7
    mixing_ndim: int = None
    diagonalization: str = None


@dataclass
class Cell:
    cell_dynamics: str = None
    press: float = None
    wmass: float = None
    cell_factor: float = None
    cell_dofree: str = None


@dataclass
class Job:
    job_type: str = 'slurm'
    nodes: int = 1
    ntasks: int = 16
    partition: str = 'general'
    time: int = 50
    memory: int = 100
    mail_type: List[str] = None  # Options: ( NONE, BEGIN, END, FAIL, REQUEUE, ALL )
    mail_user: str = None
    exec: str = 'pw.x'
    nk: int = None
    input: str = None
    output: str = None


# SISSO class NOT set up for multitask learning (MTL)
# Implemented operators: (+)(-)(*)(/)(exp)(exp-)(^-1)(^2)(^3)(sqrt)(cbrt)(log)(|-|)(scd)(^6)(sin)(cos)
@dataclass
class SISSO:
    prefix: str = None
    ntasks: int = 20
    partition: str = 'nova'
    time: int = 50
    mem: int = 100
    mail_type: List[str] = None  # Options: ( NONE, BEGIN, END, FAIL, REQUEUE, ALL )
    mail_user: str = None

    ptype: int = 1  # 1: regression, 2: classification
    desc_dim: int = 3  # Dimension of descriptor, hyperparameter
    nsample: int = None  # Number of samples in train.dat
    restart: int = 0  # 0: starts from scratch, 1: continues the job (CONTINUE file)
    nsf: int = None  # Number of scalar features in train.dat
    ops: str = '(+)(-)(*)(/)'  # operators used when combining features
    fcomplexity: int = 3  # Maximum feature complexity (# of operators in a feature, usually 0 to 7)
    funit: str = None
    fmax_min: float = 1e-3  # Feature discarded if max. abs. value < fmax_min
    fmax_max: float = 1e5  # Feature discarded if max. abs. value > fmax_max
    nf_sis: int = 20  # Number of features in each SIS-selected subspace
    method_so: str = 'L0'
    nl1l0: float = 1  # Only used if method_so = 'L1L0', number of LASSO-selected features for the L0
    fit_intercept: Union[bool, str] = '.true.'  # Fit intercept for linear model
    metric: str = 'RMSE'  # Metric for model selection for regression: RMSE or MaxAE (max. abs. error)
    nmodels: int = 100  # Number of top-ranked models to output (see 'models' folder)


def position(geometry: Union[Type[Atom], Type[Atoms]] = None) -> Tuple[int, int, str]:

    atomic_positions = ''
    positions = geometry.get_positions().tolist()
    symbols = geometry.get_chemical_symbols()
    unique_symbols = list(set(symbols))
    atom_count = len(positions)

    for atom_set in zip(symbols, positions):
        atomic_positions += f'   {atom_set[0]}\t{np.round(atom_set[1][0], 8):.8f}'
        atomic_positions += f'\t{np.round(atom_set[1][1], 8):.8f}\t{np.round(atom_set[1][2], 8):.8f}\n'

    return atom_count, len(unique_symbols), atomic_positions
    # nat, ntyp, atomic_positions


def species(geometry: Union[Type[Atom], Type[Atoms]] = None, pseudo_dir: str = None) -> List[List[str]]:

    symbols = geometry.get_chemical_symbols()
    unique_symbols = sorted(list(set(symbols)))

    list_upf = flt(os.listdir(pseudo_dir), '*.[Uu][Pp][Ff]')
    species_list = []

    for symbol in unique_symbols:

        r = re.compile(rf'{symbol}[_|.|-]\S+\Z', flags=re.IGNORECASE)
        match = list(filter(r.match, list_upf))[0]
        mw_species = molarmass_df.loc[symbol][0]

        species_list.append([symbol, mw_species, match])

    return species_list


def cell_parameters(geometry: Union[Type[Atom], Type[Atoms]] = None) -> str:

    supercell = geometry.get_cell()
    cell_string = ''

    for dimension in supercell:
        cell_string += f'{dimension[0]:.14f}\t{dimension[1]:.14f}\t{dimension[2]:.14f}\n'

    return cell_string


def lock_atoms(lock: Union[str, Tuple[int]] = None, which: Tuple[int] = (0, 0, 0), positions: str = None) -> str:

    position_index = list(range(len(positions.splitlines())))

    if 'first' in lock:
        lock = lock.lstrip('first')
        lock = tuple(position_index[:int(lock) + 1])
    elif 'last' in lock:
        lock = lock.lstrip('last')
        lock = tuple(position_index[-int(lock):])

    new_positions = []
    for index, line in enumerate(positions.splitlines()):
        if index in lock:
            line = re.sub(r' \d \d \d', '', line)
            for value in which:
                line += f' {value}'

        new_positions.append(line)

    new_positions = '\n'.join(new_positions)

    return new_positions


def parse_sisso_eqn(folder: str = '') -> pd.DataFrame:

    with open(os.path.join(folder, 'SISSO.in'), 'r') as handle:
        sisso_content = handle.read()

    desc_dim = int(list(re.finditer(r'desc_dim=\d+(?=\s+)', sisso_content))[0][0].replace('desc_dim=', ''))
    nmodels = int(list(re.finditer(r'nmodels=\d+(?=\s+)', sisso_content))[0][0].replace('nmodels=', ''))

    top_models_file = f'models/top{nmodels:04d}_{desc_dim:03d}d'
    top_models_coeff_file = f'models/top{nmodels:04d}_{desc_dim:03d}d_coeff'

    with open(os.path.join(folder, 'SIS_subspaces/Uspace.expressions'), 'r') as handle:
        content = handle.readlines()

    equ_dict = {}
    for i, line in enumerate(content):
        feature = list(re.finditer(r'.*(?=\s+corr)', line, flags=re.S))[0][0]
        feature = feature.replace('^', '**')
        equ_dict[i + 1] = feature

    with open(os.path.join(folder, top_models_file), 'r') as handle:
        top_models_cont = handle.readlines()

    equ_df = pd.DataFrame(columns=['Rank', 'RMSE', 'MaxAE', 'Feature_ID', 'intercept', 'coeff', 'equation'])
    top_models_cont.pop(0)

    for i, line in enumerate(top_models_cont):
        line = line.replace('(', '').replace(')', '')
        array = np.fromstring(line, sep='\t')
        rank, rmse, maxae, *feature_id = array
        rank = rank.astype(int)
        feature_id = np.array(feature_id).astype(int)
        equ_df.loc[i, 'Rank'] = rank
        equ_df.loc[i, 'RMSE'] = rmse
        equ_df.loc[i, 'MaxAE'] = maxae
        equ_df.loc[i, 'Feature_ID'] = feature_id

    with open(os.path.join(folder, top_models_coeff_file), 'r') as handle:
        top_models_coeff_cont = handle.readlines()

    top_models_coeff_cont.pop(0)
    for i, line in enumerate(top_models_coeff_cont):
        line = re.sub(r'\A\s+\d+\s+', '', line)
        line = np.fromstring(line, sep=' ')
        equ_df.loc[i, 'intercept'] = line[0]
        equ_df.loc[i, 'coeff'] = line[1:]

    for i, row in enumerate(equ_df.iterrows()):
        info = row[1]
        equation = str(info['intercept'])
        for feature_id, coeff in zip(info['Feature_ID'], info['coeff']):
            if coeff < 0:
                sign = '-'
            else:
                sign = '+'
            equation += ''.join([sign, str(np.abs(coeff)), '*', equ_dict[feature_id]])
        equ_df.loc[i, 'equation'] = equation

    final_df = equ_df[['RMSE', 'MaxAE', 'equation']]

    return final_df

