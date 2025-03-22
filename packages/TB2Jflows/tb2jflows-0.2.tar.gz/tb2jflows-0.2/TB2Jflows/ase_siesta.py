import copy
import json
import os
from pathlib import Path

import ase
from ase.io.jsonio import decode, encode
from pyDFTutils.siesta import MySiesta
from TB2J.interfaces import gen_exchange_siesta
from TB2J.io_merge import merge
from TB2J.rotate_atoms import rotate_atom_spin, rotate_atom_xyz


class SiestaFlow:
    def __init__(
        self,
        atoms,
        basis_set: str = "DZP",
        xc: str = "PBEsol",
        spin: str = "collinear",
        kpts=[6, 6, 6],
        Udict: dict = {},
        root_path="./",
        restart=True,
        metadata={},
        fdf_arguments={},
        relax_arguments={},
        split_soc=False,
        **kwargs,
    ):
        self.atoms = atoms
        self.basis_set = basis_set
        self.xc = xc
        self.kpts = kpts
        self.Udict = Udict
        # default fdf arguments
        self.fdf_arguments = {
            "MaxSCFIterations": 350,
            "SCF.Mixer.Method": "Pulay",
            "SCF.Mixer.History": 16,
            "SCF.Mixer.Weight": 0.4,
            "SCF.Mix.Spin": "sum",
            "SCF.DM.Tolerance": 1e-4,
            "SCF.EDM.Tolerance": "1e-2 eV",
            "SCF.H.Tolerance": "1e-3 eV",
            "Diag.ParallelOverK": "True",
        }
        if fdf_arguments:
            self.fdf_arguments.update(fdf_arguments)
        self.spin = spin
        self.root_path = root_path
        self.restart = restart
        self.kwargs = kwargs
        self.relax_args = relax_arguments

        # paths
        self.metadata_path = os.path.join(self.root_path, "metadata.json")
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)
        self.relax_path = os.path.join(self.root_path, "relax")
        self.scf_path = os.path.join(self.root_path, "scf")

        self.relaxed_atoms = None
        self.split_soc = split_soc
        self.initialize_metadata(metadata)

    def initialize_metadata(self, metadata):
        """Initialize the metadata.
        If already exist, read from it.

        """
        if (
            self.restart
            and os.path.exists(self.metadata_path)
            and os.path.isfile(self.metadata_path)
        ):
            self.load_metadata()
        else:
            self.metadata = {
                "root_path": self.root_path,
                "calculator": "siesta",
                "initial_atoms": encode(self.atoms),
                "spin": self.spin,
                "xc": self.xc,
                "already_relaxed": False,
            }
            self.metadata.update(metadata)

    def load_metadata(self):
        with open(self.metadata_path, "r") as myfile:
            self.metadata = json.load(myfile)
            self.initial_atoms = decode(self.metadata["initial_atoms"])
            if ("relaxed_atoms" in self.metadata) and (
                self.metadata["relaxed_atoms"] is not None
            ):
                self.relaxed_atoms = decode(self.metadata["relaxed_atoms"])

    def write_metadata(self):
        with open(self.metadata_path, "w") as myfile:
            json.dump(self.metadata, myfile)

    def update_metadata(self, d):
        self.initialize_metadata(d)
        self.write_metadata()

    @property
    def spin(self):
        return self._spin

    @spin.setter
    def spin(self, spin):
        self._spin = spin
        if spin == "spin-orbit":
            self.fdf_arguments.update({"SCF.Mix": "hamiltonian", "WriteOrbMom": True})
        else:
            if "writeOrbMom" in self.fdf_arguments:
                self.fdf_arguments.pop("WriteOrbMom")
        if spin == "spin-orbit":
            self.rel = "fr"
        else:
            self.rel = "sr"

    def get_calculator(
        self,
        atoms: ase.Atoms,
        path="./",
        label="siesta",
        fdf_arguments={},
    ):
        fdf_args = copy.deepcopy(self.fdf_arguments)
        fdf_args.update(fdf_arguments)
        calc = MySiesta(
            atoms=atoms,
            label=label,
            xc=self.xc,
            basis_set=self.basis_set,
            kpts=self.kpts,
            spin=self.spin,
            fdf_arguments=fdf_args,
            **self.kwargs,
        )
        if self.Udict:
            # calc.set_Hubbard_U(self.Udict)
            calc.set_Udict(self.Udict)
        calc.directory = path
        calc.atoms = atoms
        return copy.deepcopy(calc)

    def relax(
        self,
        atoms,
        use_collinear=True,
        path="./relax",
        label="siesta",
        TypeOfRun="Broyden",
        VariableCell=True,
        ConstantVolume=False,
        RelaxCellOnly=False,
        MaxForceTol=0.001,
        MaxStressTol=0.1,
        NumCGSteps=200,
    ):
        print(f"Relaxation in {path}")
        if (
            self.restart
            and self.metadata["already_relaxed"]
            and self.relaxed_atoms is not None
        ):
            self.load_metadata()
            atoms = self.relaxed_atoms
        else:
            old_spin = self.spin
            if use_collinear:
                self.spin = "collinear"
            calc = self.get_calculator(atoms, path=self.relax_path, label=label)
            calc.atoms = atoms
            atoms = calc.relax(
                atoms,
                TypeOfRun=TypeOfRun,
                VariableCell=VariableCell,
                ConstantVolume=ConstantVolume,
                RelaxCellOnly=RelaxCellOnly,
                MaxForceTol=MaxForceTol,
                MaxStressTol=MaxStressTol,
                NumCGSteps=NumCGSteps,
            )
            self.spin = old_spin
            self.relaxed_atoms = atoms
            self.update_metadata(
                {
                    "already_relaxed": True,
                    "relax_path": self.relax_path,
                    "relaxed_atoms": encode(self.relaxed_atoms),
                }
            )
        return atoms

    def scf_calculation(self, atoms, path="./scf", label="siesta"):
        print(f"SCF calculation in {path}")
        HS_args = {
            "SaveHS": True,
            #'CDF.Save': True,
            #'CDF.Compress': 9,
        }
        calc = self.get_calculator(atoms, path=path, label=label, fdf_arguments=HS_args)
        calc.get_potential_energy()

    def scf_calculation_with_rotations(
        self, atoms, label="siesta", rotate_type="structure"
    ):
        self.fdf_arguments["Spin.Fix"] = False
        self.spin = "spin-orbit"
        if rotate_type == "structure":
            atoms_xyz = rotate_atom_xyz(atoms)
        elif rotate_type == "spin":
            atoms_xyz = rotate_atom_spin(atoms)
        else:
            raise NotImplementedError(f"rotate_type={rotate_type} is not implemented")
        for ratoms, rot in zip(atoms_xyz, ("x", "y", "z")):
            self.scf_calculation(
                ratoms, path=os.path.join(self.scf_path, rot), label=label
            )

    def scf_calculation_single_noncollinear(self, atoms, label="siesta"):
        self.fdf_arguments["Spin.Fix"] = False
        self.scf_calculation(
            atoms, path=os.path.join(self.scf_path, "single_noncollinear"), label=label
        )

    def scf_calculatoin_split_soc(self, atoms, label="siesta", nscf=False):
        fdf_args = {
            "SOC_split_SR_SO": True,
            # "Spin.OrbitStrength": 3,
            "SaveHS.so": True,
            "SaveHS": True,
            "Spin.Fix": False,
        }
        nscf_args = {
            "SCF.DM.Converge": True,
            "SCF.DM.Tolerance": 1e4,
            "SCF.H.Converge": False,
            "SCF.EDM.Converge": False,
            "SCF.Mix.First": False,
            "SCF.Mix": "density",
            "MaxSCFIterations": 1,
        }
        if nscf:
            fdf_args.update(nscf_args)

        self.spin = "spin-orbit"
        path = Path(self.scf_path) / "split_soc"
        path.mkdir(parents=True, exist_ok=True)
        collinear_path = Path(self.scf_path) / "collinear"
        # density matrix from collinear calculation
        # copy density matrix from collinear calculation
        dmfile = collinear_path / f"{label}.DM"
        if dmfile.exists():
            dmfile_new = path / f"{label}.DM"
            print(f"Copying {dmfile} to {dmfile_new}")
            os.system(f"cp {dmfile} {dmfile_new}")
        calc = self.get_calculator(
            atoms, path=path, label=label, fdf_arguments=fdf_args
        )
        calc.get_potential_energy()

    def scf_calculation_collinear(self, atoms, label="siesta"):
        old_spin = self.spin
        self.spin = "collinear"
        self.scf_calculation(
            atoms, path=os.path.join(self.scf_path, "collinear"), label=label
        )
        self.spin = old_spin

    def run_TB2J_collinear(self, **kwargs):
        path = os.path.join(self.scf_path, "collinear")
        fdf_fname = os.path.join(path, "siesta.fdf")
        gen_exchange_siesta(
            fdf_fname=fdf_fname,
            **kwargs,
            output_path=os.path.join(self.root_path, "TB2J_results_collinear"),
        )

    def run_TB2J_single_noncollinear(self, **kwargs):
        path = os.path.join(self.scf_path, "single_noncollinear")
        fdf_fname = os.path.join(path, "siesta.fdf")
        gen_exchange_siesta(
            fdf_fname=fdf_fname,
            **kwargs,
            output_path=os.path.join(
                self.root_path, "TB2J_results_single_noncollinear"
            ),
        )

    def set_nonscf_params(self):
        nscf_params = {
            "SCF.DM.Converge": False,
            "SCF.DM.Tolerance": 1e4,
            "SCF.H.Converge": False,
            "SCF.EDM.Converge": False,
            "SCF.Mix.First": False,
            "SCF.Mix": "density",
            "MaxSCFIterations": 1,
        }

        self.fdf_arguments.update(nscf_params)

    def run_TB2J_split_soc(self, **kwargs):
        path = os.path.join(self.scf_path, "split_soc")
        fdf_fname = os.path.join(path, "siesta.fdf")
        gen_exchange_siesta(
            fdf_fname=fdf_fname,
            read_H_soc=True,
            **kwargs,
            output_path=os.path.join(self.root_path, "TB2J_results_split_soc"),
        )
        # merge results
        paths = [
            os.path.join(self.root_path, f"TB2J_results_split_soc_{rot}")
            for rot in ("x", "y", "z")
        ]
        merge(
            *paths,
            # method=rotate_type,
            write_path=os.path.join(self.root_path, "TB2J_results_merged"),
        )

    def run_TB2J(self, skip=False, **kwargs):
        paths = []
        for rot in ("x", "y", "z"):
            path = os.path.join(self.scf_path, rot)
            paths.append(path)
            TB2J_path = os.path.join(self.root_path, f"TB2J_results_{rot}")
            if not (skip and os.path.exists(os.path.join(TB2J_path, "exchange.txt"))):
                fdf_fname = os.path.join(path, "siesta.fdf")
                gen_exchange_siesta(
                    fdf_fname=fdf_fname, **kwargs, output_path=TB2J_path
                )

    def run_TB2J_rotate_structure(self, skip=False, **kwargs):
        paths = []
        for rot in ("x", "y", "z"):
            path = os.path.join(self.scf_path, rot)
            paths.append(path)
            TB2J_path = os.path.join(self.root_path, f"TB2J_results_{rot}")
            if not (skip and os.path.exists(os.path.join(TB2J_path, "exchange.txt"))):
                fdf_fname = os.path.join(path, "siesta.fdf")
                gen_exchange_siesta(
                    fdf_fname=fdf_fname, **kwargs, output_path=TB2J_path
                )

    def run_TB2J_merge(self, rotate_type="structure"):
        paths = [
            os.path.join(self.root_path, f"TB2J_results_{rot}")
            for rot in ("x", "y", "z")
        ]
        merge(
            *paths,
            # method=rotate_type,
            write_path=os.path.join(self.root_path, "TB2J_results_merged"),
        )

    def runall_collinear(self, atoms, relax=True, scf=True, TB2J=True,  **kwargs):
        if relax:
            atoms = self.relax(atoms, **self.relax_args)
        if scf:
            self.scf_calculation_collinear(atoms, label="siesta")
        if TB2J:
            self.run_TB2J_collinear(**kwargs)

    def runall_nc(
        self, atoms, relax=True, scf=True, TB2J=True, rotate_type="structure", **kwargs
    ):
        if relax:
            atoms = self.relax(atoms, **self.relax_args)
        if scf:
            self.scf_calculation_with_rotations(
                atoms, rotate_type=rotate_type, label="siesta"
            )
        if TB2J:
            self.run_TB2J(**kwargs)
            self.run_TB2J_merge(rotate_type=rotate_type)

    def runall_split_soc(self, atoms, relax=True, scf=True, TB2J=True, **kwargs):
        if relax:
            atoms = self.relax(atoms, **self.relax_args)
        if scf:
            self.scf_calculatoin_split_soc(atoms, label="siesta")
        if TB2J:
            self.run_TB2J_split_soc(**kwargs)

    def runall(
        self, atoms, relax=True, scf=True, TB2J=True, rotate_type="structure", **kwargs
    ):
        if self.spin == "collinear":
            self.runall_collinear(atoms, relax=relax, scf=scf, TB2J=TB2J, **kwargs)
        elif self.spin == "spin-orbit+onsite":
            self.runall_nc(
                atoms,
                relax=relax,
                scf=scf,
                TB2J=TB2J,
                rotate_type=rotate_type,
                **kwargs,
            )

        elif self.spin == "spin-orbit":
            if self.split_soc:
                self.runall_split_soc(atoms, relax=relax, scf=scf, TB2J=TB2J, **kwargs)
            else:
                self.runall_nc(
                    atoms,
                    relax=relax,
                    scf=scf,
                    TB2J=TB2J,
                    rotate_type=rotate_type,
                    **kwargs,
                )
        elif self.spin == "collinear+spin-orbit":
            self.runall_collinear(atoms, relax=relax, scf=scf, TB2J=TB2J, **kwargs)
            if self.split_soc:
                self.runall_split_soc(atoms, relax=relax, scf=scf, TB2J=TB2J, **kwargs)
            else:
                self.runall_nc(
                    atoms,
                    relax=relax,
                    scf=scf,
                    TB2J=TB2J,
                    rotate_type=rotate_type,
                    **kwargs,
                )
        else:
            raise NotImplementedError(f"spin={self.spin} is not implemented in runall")
