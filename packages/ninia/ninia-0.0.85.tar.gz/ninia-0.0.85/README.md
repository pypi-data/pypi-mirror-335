# Ninia

A small Python wrapper for setting up Quantum Espresso input files. More functionality may be added later.

<p>Currently, there is only assumed support for hexagonal close packed (HCP) crystal structures. 
Support for other structures may be tested but <b>should not</b> be expected.</p>

> Note: The ```calc.create_bash()``` function (described later) assumes a Torque/PBS structure and sets up script to run in parallel using MPI. It also assumes an already built Quantum Espresso package and that ```pw.x``` can be run from the command-line. 
> 
> For tips on how to install Quantum Espresso on an HPC cluster, go to [Espresso Installation](/espresso_installation.md).

---

### Behind the Name
![Ninia - Coffee Snake](Images/Ninia_atrata.jpg "Ninia - Coffee Snake")

**Ninia** is a genus of snakes, also known as **coffee snakes**, that are native to parts of Central and South America. The choice of name is a play on **Python** and Quantum **Espresso**.

---
#### Example usage:

```python
# Import necessary modules:
from ase.build import molecule, add_adsorbate, hcp0001
from ase.visualize import view

# Set up geometry using ASE:
surface = hcp0001('Ru', size=(4, 2, 4), a=2.7059, c=4.2815)
ad = molecule('NH2')
ad.rotate(180, 'x')
add_adsorbate(surface, ad, 2.0, 'hcp')

view(surface, viewer='x3d')  # Specific viewer for use in Jupyter
```
<p>This will display a view of the geometry we have created. More information
about ASE (Atomic Simulation Environment) can be found at their homepage:
<a href="https://wiki.fysik.dtu.dk/ase/">https://wiki.fysik.dtu.dk/ase/</a></p>

Then you can start using ninia to convert this geometry into an input file:
```python
from ninia import relax
calc = relax.Relax(prefix='Ru_test', functional='beef')
calc.set_directories(outputdir='/home/ajs0201/workQE/output',
                     pseudodir='/home/ajs0201/workQE/pseudo')
# Ninia assumes the current script directory as the input directory
# if none is given.
calc.load_geometry(surface)
calc.set_parameters(mixing_beta=0.15)

calc.create_input()
calc.create_job(hours=20)
# This will create both an input (.i) file and bash (.sh) for the geometry above
```
---
If you do not specify the **prefix** and **functional** during the initialization step, the program will give warnings. Additionally, the pseudopotential directory ***must*** be set before the ```calc.load_geometry()``` step.

In the ```calc.set_directories()``` step, you can set the following directories:
* The directory to place input and bash files (**inputdir**)
* The directory to place output files created by Quantum Espresso (**outputdir**)
* The directory that contains pseudopotentials relevant to the calculation (**pseudodir**)
> Note: The output directory, post calculation, will contain wave function files (.wfc) and save directories (.save/). This ***does not*** include output files (.out), which will be place in the input directory, unless explicitly changed.

In the ```calc.set_parameters()``` step, you can set the following parameters [default]:
* Plane wave cutoff energy (ecutwfc) [30.0]
* Plane wave cutoff density (ecutrho) [4*ecutwfc]
* Convergence threshold (conv_thr) [1e-8]
* Electron mixing beta (mixing_beta) [0.7]
* Number of k-points (k_points) [[4, 4, 4, 0, 0, 0]]
* Functional (functional) [beef]

In the ```calc.create_job()``` step, you can set the following parameters [default]:
* Job type [```pbs.sh```] (other option ```slurm.sh```)
* Partition/queue [```general```]
* Memory used by calculation in GB (memory) [50]
* Number of CPUs used by calculation (cpus) [8]
* Walltime allowed for execution in hours (hours) [30]

