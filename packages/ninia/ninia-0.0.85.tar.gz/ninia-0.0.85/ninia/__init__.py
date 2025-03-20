# Copyright 2022 Alex Summers
# See LICENSE file for more information

import sys

if sys.version_info[0] == 2:
    raise ImportError('Ninia requires Python 3.7. This is Python 2.')

__all__ = ['Relax', 'parse_sisso_eqn', 'gen_sisso', 'run_sisso']
__version__ = '0.0.85'

from ninia.relax import Relax
from ninia.sisso import gen_sisso, run_sisso
from ninia.utils import parse_sisso_eqn

