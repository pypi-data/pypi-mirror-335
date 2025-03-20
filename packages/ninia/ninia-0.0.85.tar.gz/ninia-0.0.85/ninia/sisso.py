"""
Alex Summers
Script to create single-task SISSO configurations
"""

from ninia.utils import SISSO
from typing import Type, Union, List, Tuple
from jinja2 import Environment, BaseLoader
import pkg_resources
import pandas as pd
import numpy as np
import subprocess
import os

starting_dir = os.getcwd()

sisso_string = pkg_resources.resource_string(__name__, 'input/SISSO.in.jinja2')
sisso_template = Environment(loader=BaseLoader).from_string(sisso_string.decode('utf-8'))
slurm_string = pkg_resources.resource_string(__name__, 'input/SISSO_job.sh.jinja2')
slurm_template = Environment(loader=BaseLoader).from_string(slurm_string.decode('utf-8'))


def gen_sisso(sisso: Type[SISSO] = SISSO(), train_data: pd.DataFrame = None,
              feature_unit: Union[pd.DataFrame, np.ndarray] = None, folder: str = None) -> None:

    if train_data is None:
        raise RuntimeError('Training data (train_data) is required for SISSO.')
    if (sisso.funit is None) and (feature_unit is None):
        raise RuntimeWarning('Recommended to set relative feature units either through sisso.funit or feature_unit.')

    # Generate new folder if needed, cd to folder
    if folder is not None:
        if not os.path.exists(os.path.join(starting_dir, folder)):
            os.mkdir(folder)

        # Change directory to folder
        os.chdir(folder)

    current_dir = os.getcwd()  # To send to folder for sisso_template

    # Setting remaining parameters for sisso object
    if sisso.prefix is None:
        sisso.prefix = 'SISSO'

    n_sample, n_feat = train_data.shape
    sisso.nsample = n_sample
    sisso.nsf = n_feat - 1

    # Writing sisso_template and #slurm_template
    sisso_rendered = sisso_template.render(sisso=sisso)
    slurm_rendered = slurm_template.render(sisso=sisso, folder=current_dir)
    with open('SISSO.in', 'w') as handle:
        handle.write(sisso_rendered)
    with open(f'{sisso.prefix}.sh', 'w') as handle:
        handle.write(slurm_rendered)

    train_data.to_csv('train.dat', sep='\t', index_label='samples')

    if feature_unit is not None:
        n_feat_check, _ = feature_unit.shape
        if n_feat_check != sisso.nsf:
            raise RuntimeWarning('Warning: Number of features do not match between train_data and feature_unit.')

        feature_unit.to_csv('feature_unit', index=False, header=False, sep='\t')

    os.chdir(starting_dir)


def run_sisso(sisso: Type[SISSO] = SISSO(), train_data: pd.DataFrame = None,
              feature_unit: Union[pd.DataFrame, np.ndarray] = None, folder: str = None) -> None:

    if train_data is None:
        raise RuntimeError('Training data (train_data) is required for SISSO.')
    if (sisso.funit is None) and (feature_unit is None):
        raise RuntimeWarning('Recommended to set relative feature units either through sisso.funit or feature_unit.')

    # Generate new folder if needed, cd to folder
    if folder is not None:
        if not os.path.exists(os.path.join(starting_dir, folder)):
            os.mkdir(folder)

        # Change directory to folder
        os.chdir(folder)

    current_dir = os.getcwd()  # To send to folder for sisso_template

    # Setting remaining parameters for sisso object
    if sisso.prefix is None:
        sisso.prefix = 'SISSO'

    n_sample, n_feat = train_data.shape
    sisso.nsample = n_sample
    sisso.nsf = n_feat - 1

    # Writing sisso_template and #slurm_template
    sisso_rendered = sisso_template.render(sisso=sisso)
    with open('SISSO.in', 'w') as handle:
        handle.write(sisso_rendered)

    train_data.to_csv('train.dat', sep='\t', index_label='samples')

    if feature_unit is not None:
        n_feat_check, _ = feature_unit.shape
        if n_feat_check != sisso.nsf:
            raise RuntimeWarning('Warning: Number of features do not match between train_data and feature_unit.')

        feature_unit.to_csv('feature_unit', index=False, header=False, sep='\t')

    subprocess.run(f'mpirun -n {sisso.ntasks} SISSO > log', shell=True)
    os.chdir(starting_dir)

