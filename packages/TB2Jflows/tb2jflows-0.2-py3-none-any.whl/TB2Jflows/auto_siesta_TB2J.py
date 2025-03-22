#!/usr/bin/env python3
import numpy as np
from ase.io import read
from ase.units import Ry

from TB2Jflows import SiestaFlow


def atoms_mag_along_z(atoms, mag, toz=True):
    symbols = atoms.get_chemical_symbols()
    symbols = np.array(symbols)

    norm = np.linalg.norm(mag, axis=1)
    imaxmag = np.argmax(norm)
    ipolarized = np.where(norm > 0.1)

    elems = set(symbols[ipolarized])

    # rotate to collinear
    if toz:
        m_col = np.zeros(mag.shape[0], dtype=float)
        m_ref = mag[imaxmag]
        for i, m in enumerate(mag):
            mrot = m @ m_ref
            n = np.linalg.norm(m)
            m_col[i] = n if mrot > 0 else -n
        atoms.set_initial_magnetic_moments(None)
    else:
        atoms.set_initial_magnetic_moments(mag)
    return atoms, elems


def read_to_collinear_mag_atoms(name):
    path = f"../structures/{name}"
    mag = np.load(f"{path}/mag.npy")
    atoms = read(f"{path}/POSCAR.vasp")
    atoms, elems = atoms_mag_along_z(atoms, mag)
    return atoms, elems


def auto_siesta_TB2J(
    path,
    atoms,
    spin,
    elems,
    Udict={},
    xc="PBE",
    kmesh=None,
    split_soc=False,
    relax=False,
    scf=True,
    TB2J=True,
    rotate_type="structure",
    fincore=True,
    relax_kwargs={},
    siesta_kwargs={},
    TB2J_kwargs={},
    fdf_kwargs={},
):
    # mag_elems = list(elems)
    symbols = atoms.get_chemical_symbols()
    cell = atoms.get_cell_lengths_and_angles()
    Uname = {}
    sset = set()
    for s in symbols:
        if s not in sset:
            sset.add(s)
            Uname[s] = s + f".{len(sset)}"
    if kmesh is None:
        kmesh = [int(40 // cell[0] + 1), int(40 // cell[1] + 1), int(40 // cell[2] + 1)]

    fdf_arguments = {
        "SCF.DM.Tolerance": "0.0001",
        "ElectronicTemperature": "100 K",
        "SCF.Mixer.Weight": "0.1",
        "SCF.Mixer.History": "16",
        "SCF.Mix.Spin": "sum",
        "DM.NumberPulay": "6",
        "SCF.Mixer.Method": "Pulay",
        "MaxSCFIterations": 500,
        "SCF.MustConverge": "False",
        "SCFMustConverge": "False",
        "WriteMullikenPop": "1",
        "MullikenInSCF": "True",
        "WriteHirshfeldPop": "True",
        "WriteVoronoiPop": "True",
        "CDF.save": "True",
    }
    fdf_arguments.update(fdf_kwargs)
    flow = SiestaFlow(
        atoms=atoms,
        xc=xc,
        spin=spin,
        restart=True,
        root_path=path,
        kpts=kmesh,
        mesh_cutoff=600 * Ry,
        energy_shift=0.1,
        fdf_arguments=fdf_arguments,
        fincore=fincore,
        Udict=Udict,
        split_soc=split_soc,
        relax_arguments = relax_kwargs,
        **siesta_kwargs,
    )
    flow.write_metadata()
    flow.runall(
        atoms,
        relax=relax,
        scf=scf,
        TB2J=TB2J,
        rotate_type=rotate_type,
        magnetic_elements=elems,
        **TB2J_kwargs,
    )


if __name__ == "__main__":
    atoms = None
    elems = None
    path = "./"
    auto_siesta_TB2J(
        path,
        atoms,
        spin="collinear",
        elems=elems,
        Udict={},
        kmesh=None,
        relax=False,
        scf=True,
        rotate_type="structure",
    )
