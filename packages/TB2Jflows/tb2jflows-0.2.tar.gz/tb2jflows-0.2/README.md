# TB2Jflows
Workflows for automatically calculation of exchange parameters from DFT

## Installation

First download the package from the github page. Run the following command in the TB2Jflows directory

```
pip install . --user
```

will install TB2Jflows and the dependencies.

You need the following things to 

- Siesta built with psml and netcdf.
- Pseudopotentials from PseudoDojo Dataset. 
- Configure the command to run siesta and the path to the pseudopotentials, e.g.

```
export ASE_IESTA_COMMAND="mpirun siesta < PREFIX.fdf > PREFIX.out 2> PREFIX.err"
export DOJO_PATH='$HOME/.local/pp/dojo'
```

## Usage

Below is an example of calculating the exchange parameters of SrMnO3:

```python
from ase.io import read
from TB2Jflows import SiestaFlow


def calculate_siesta_TB2J_SrMnO3():
    atoms = read('SrMnO3.STRUCT_OUT')
    atoms.set_initial_magnetic_moments([0, 3, 0, 0, 0])
    flow = SiestaFlow(atoms,
                      spin='spin-orbit',
                      restart=True,
                      root_path='SrMnO3')
    flow.write_metadata()
    atoms = flow.relax(atoms)
    flow.scf_calculation_with_rotations(atoms)
    flow.run_TB2J(magnetic_elements='Mn',
                  nz=50,
                  kmesh=[7, 7, 7],
                  Rcut=18,
                  np=10,
                  use_cache=True)
    flow.run_TB2J_merge()


if __name__ == '__main__':
    calculate_siesta_TB2J_SrMnO3()
~                                     
```

