from ase.io import read
import numpy as np
from TB2Jflows import SiestaFlow


def calculate_siesta_TB2J_SrMnO3():
    atoms = read('POSCAR')
    atoms.set_initial_magnetic_moments([0, 3, 0, 0, 0])
    flow = SiestaFlow(atoms,
                      spin='spin-orbit',
                      restart=True,
                      kpts=[6, 6, 6],
                      root_path='SrMnO3')
    flow.write_metadata()

    #atoms = flow.relax(atoms)
    mz = [0, 3, 0, 0, 0]
    #m = np.zeros((5, 3), dtype=float)
    #m[1] = np.array([3, 3, 3])/1.732
    # m[1]=np.array([0,0,3])
    # atoms.set_initial_magnetic_moments(None)
    atoms.set_initial_magnetic_moments(mz)
    # flow.scf_calculation_single_noncollinear(atoms)
    # flow.run_TB2J_single_noncollinear(magnetic_elements='Mn',
    #              nz=50,
    #              kmesh=[5, 5, 5],
    #              Rcut=18,
    #              np=3,
    #              use_cache=True)

    flow.scf_calculation_with_rotations(atoms)
    flow.run_TB2J(magnetic_elements='Mn',
                  nz=50,
                  kmesh=[7, 7, 7],
                  Rcut=18,
                  np=3,
                  use_cache=True)
    flow.run_TB2J_merge()


if __name__ == '__main__':
    calculate_siesta_TB2J_SrMnO3()
