from ase import Atoms
from ase.calculators.abacus import Abacus, AbacusProfile
from pathlib import Path
import shutil

abacus = "/home/hexu/.local/bin/abacus"
profile = AbacusProfile(argv=["mpirun", "-n", "8", abacus])


def gen_atoms():
    """
    2D Fe slab
    """
    atoms = Atoms(
        "Fe", scaled_positions=[(0, 0, 0)], cell=(2.315, 2.315, 15), pbc=(1, 1, 1)
    )
    return atoms


def gen_atoms_x():
    """
    2D Fe slab
    """
    atoms = Atoms(
        "Fe", scaled_positions=[(0, 0, 0)], cell=(15, 2.315, 2.315), pbc=(1, 1, 1)
    )
    return atoms

pdir = "/home/hexu/.local/pp/abacus/ABACUS-orbitals-main/Dojo-NC-FR"

default_params = dict(
    profile=profile,
    directory="Fe_soc0_x",
    pseudo_dir=f"{pdir}/Pseudopotential",
    orbital_dir=f"{pdir}/Orbitals/Fe/Orbital_Fe_DZP",
    pp={"Fe": "Fe.upf"},
    basis={"Fe": "Fe_gga_10au_100Ry_4s2p2d1f.orb"},
    calculation="scf",
    xc="PBE",
    kpts=(9, 9, 1),
    nspin=4,
    symmetry=0,
    noncolin=1,
    lspinorb=1,
    ecutwfc=100,
    scf_thr=1.0e-6,
    init_chg="atomic",
    out_mul=1,
    out_chg=1,
    out_dos=0,
    out_band=0,
    out_wfc_lcao=1,
    out_mat_hs2=1,  # output H(R) and S(R) matrix
    ks_solver="scalapack_gvx",
    scf_nmax=500,
    out_bandgap=0,
    basis_type="lcao",
    gamma_only=0,
    smearing_method="gaussian",
    smearing_sigma=0.01,
    mixing_type="broyden",
    mixing_beta=0.5,
    soc_lambda=1.0,
)

params_nosoc = default_params.copy()
params_nosoc.update(dict(
    soc_lambda=0.0,
    noncolin=1,
    ))

params_soc_nscf = default_params.copy()
params_soc_nscf.update(dict(
    calculation="scf",
    soc_lambda=1.0,
    init_chg="file",
    init_wfc="file",
    out_chg=0,
    out_wfc_lcao=0,
    scf_nmax=1,
    mixing_beta=1e-6,
    scf_thr=1e6,
    ))


def run_abacus(root="Fe_x", M=[[3, 0, 0]]):
    atoms = gen_atoms()
    atoms.set_initial_magnetic_moments(M)

    path0=Path(root)/"soc0"
    path1=Path(root)/"soc1"

    params = params_nosoc.copy()
    params.update(directory=path0)

    calc = Abacus(**params)
    atoms.set_calculator(calc)
    atoms.get_potential_energy()
    
    path1.mkdir(parents=True, exist_ok=True)
    if (path1/"OUT.ABACUS").exists():
        shutil.rmtree(str(path1/"OUT.ABACUS"))
    shutil.copytree(str(path0/"OUT.ABACUS"), str(path1/"OUT.ABACUS"))

    params = params_soc_nscf.copy()
    params.update(directory=path1)
    calc = Abacus(**params)
    atoms.set_calculator(calc)
    atoms.get_potential_energy()


def main():
    run_abacus("Fe_x", [[3, 0, 0]])
    run_abacus("Fe_z", [[0, 0, 3]])
    run_abacus("Fe_-z", [[0, 0, -3]])
    run_abacus("Fe_-x", [[-3, 0, 0]])


if __name__ == "__main__":
    main()
