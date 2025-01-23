import os
import numpy as np

from ase import Atoms
from ase.calculators.singlepoint import SinglePointDFTCalculator
from ase.db import connect
from ase.data import atomic_numbers, atomic_masses

class Database:
    def __init__(self):
        self.cwd = os.getcwd()

    def store(self, header_data, training_data, db_path):
        """
        Write the header data and training data to the database file.
        
        Parameters
        ----------
        header_data : dict
            A dictionary containing header information.
            Example:
            {
                "ref_energy": [0.0, 0.0],
                "mass": [140.115, 16.0],
                "basis_for_Ce": {1: [1, 2, 3, ...], ...},
                "basis_for_O": {1: [9, 10, 11, ...], ...}
            }

        training_data : list
            A list of dictionaries containing training data.
            Example:
            [
                {
                    "conf_num": 1,
                    "sys_name": "CeO2",
                    "atom_type_num": {"Ce": 8, "O": 16},
                    "ctifor": 2.000000000000000E-003,
                    "vectors": [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]],
                    "positions": [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], ...],
                    "free_energy": -123.456,
                    "forces": [[0.1, 0.2, 0.3], [-0.1, -0.2, -0.3], ...],
                    "stress": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
                },
                ...
            ]
            "stress" contains elements in the order XX, YY, ZZ, XY, YZ, ZX.

        db_path : str
            Path to ASE database file to be written.

        Notes
        -----
        Each "row" in the ase database file contains the following information:
        {
            "sys_name": "CeO2",
            "conf_num": 1,
            "ctifor": 0.002,
            "numbers": [58, ..., 58, 8, ..., 8],
            "positions": [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], ...],
            "cell": [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]],
            "pbc": [True, True, True],
            "calculator": "vasp",
            "free_energy": -123.456,
            "forces": [[0.1, 0.2, 0.3], [-0.1, -0.2, -0.3], ...],
            "stress": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],

            "data": {
                "basis": {"Ce": [1, 2, 3, ...], "O": [9, 10, 11, ...]},
                "ref_energy": [0.0, 0.0],
                "mass": [140.115, 16.0]
                }
        }
        """
        self.header_data = header_data
        self.training_data = training_data

        db = connect(db_path)

        ref_energy = self.header_data["ref_energy"]
        mass = self.header_data["mass"]
        for data in self.training_data:
            chemical_symbols = [element for element, n in data["atom_type_num"].items() for _ in range(n)]
            vectors = data["vectors"]
            positions = data["positions"]

            atoms = Atoms(
                chemical_symbols,
                cell=vectors,
                positions=positions,
                pbc=True
                )

            free_energy = data["free_energy"]
            forces = data["forces"]
            stress = data["stress"]

            calculator = SinglePointDFTCalculator(
                atoms,
                free_energy=free_energy,
                forces=forces,
                stress=stress
                )

            atoms.set_calculator(calculator)
            atoms.calc.name = "vasp"

            sys_name = str(data["sys_name"])
            conf_num = int(data["conf_num"])
            ctifor = float(data["ctifor"])

            basis = {}
            element_list = list(data["atom_type_num"].keys())
            for element in element_list:
                basis_key = f"basis_for_{element}"
                if basis_key in self.header_data:
                    basis_value = self.header_data[basis_key].get(conf_num, [])
                    basis[element] = basis_value
                else:
                    basis[element] = []

            db.write(
                atoms,
                sys_name=sys_name,
                conf_num=conf_num,
                ctifor=ctifor,
                data={
                    "basis": basis,
                    "ref_energy": ref_energy,
                    "mass": mass
                    }
                )



    def load(self, db_path, ref_energy=None, mass=None):
        """
        Read the header data and training data from the database file.

        Parameters
        ----------
        db_path : str
            Path to ASE database file to be loaded.
        ref_energy : list, optional
            Reference energy for each atom type.
            Default is None.
        mass : list, optional
            Mass for each atom type.
            Default is None.

        Returns
        -------
        header_data : dict
            A dictionary containing header information.
            Example:
            {
                "n_conf": 3,
                "max_n_atom_type": 2,
                "all_atom_type": ["Ce", "O"],
                "max_n_atom_per_sys": 24,
                "max_n_atom_per_type": 16,
                "ref_energy": [0.0, 0.0],
                "mass": [140.115, 16.0],
                "n_basis": {'Ce': 10, 'O': 20},
                "basis_for_Ce": {1: [1, 2, 3, ...], ...},
                "basis_for_O": {1: [9, 10, 11, ...], ...}
            }

        training_data : list
            A list of dictionaries containing training data.
            Example:
            [
                {
                    "conf_num": 1,
                    "sys_name": "CeO2",
                    "atom_type_num": {"Ce": 8, "O": 16},
                    "ctifor": 0.002,
                    "vectors": [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]],
                    "positions": [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], ...],
                    "free_energy": -123.456,
                    "forces": [[0.1, 0.2, 0.3], [-0.1, -0.2, -0.3], ...],
                    "stress": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
                },
                ...
            ]
            "stress" contains elements in the order XX, YY, ZZ, XY, YZ, ZX.
        """
        self.ref_energy = ref_energy
        self.mass = mass

        db = connect(db_path)

        header_data = {}
        training_data = []

        conf_num = 0
        max_n_atom_type = 0
        all_atom_type = []
        max_n_atom_per_sys = 0
        max_n_atom_per_type = 0
        n_basis = {}
        all_basis = {}
        for row in db.select():
            conf_num += 1
            try:
                #sys_name = row["sys_name"] # Both are OK
                sys_name = row.sys_name
            except:
                sys_name = "Undefined"

            atoms = row.toatoms()
            chemical_symbols = atoms.get_chemical_symbols()
            n_atom_type = len(set(chemical_symbols))
            n_atom = len(chemical_symbols)

            atom_type_num = {}
            for element in chemical_symbols:
                if element in atom_type_num:
                    atom_type_num[element] += 1
                else:
                    atom_type_num[element] = 1

            try:
                basis = row.data.basis # Dictionary; {element: [basis]}
            except:
                basis = {}
                for element in atom_type_num.keys():
                    basis[element] = []

            try:
                ctifor = row.ctifor
            except:
                ctifor = 0.002 # Default value of ML_CTIFOR in VASP

            vectors = row.cell.tolist()
            positions = row.positions.tolist()
            # The "energy" in the ML_ABN file corresponds to the "free energy" in the OUTCAR file, 
            # so it is registered as "free energy" in the atoms object.
            # On the other hand, variables and keys conform to the ML_ABN file 
            # and are represented as "energy".
            free_energy = row.free_energy
            forces = row.forces.tolist()
            stress = row.stress.tolist()

            training_data.append({
                "conf_num": conf_num,
                "sys_name": sys_name,
                "atom_type_num": atom_type_num,
                "ctifor": ctifor,
                "vectors": vectors,
                "positions": positions,
                "free_energy": free_energy,
                "forces": forces,
                "stress": stress
                })

            # Get header data
            if n_atom_type > max_n_atom_type:
                max_n_atom_type = n_atom_type

            for element in atom_type_num.keys():
                if element not in all_atom_type:
                    all_atom_type.append(element)

                # Count basis data
                if element in n_basis:
                    n_basis[element] += len(basis[element])
                else:
                    n_basis[element] = len(basis[element])

                # Get basis data
                basis_tag = f"basis_for_{element}"
                if basis_tag not in all_basis:
                    all_basis[basis_tag] = {}

                if len(basis[element]) > 0:
                    all_basis[basis_tag][conf_num] = basis[element]

            if n_atom > max_n_atom_per_sys:
                max_n_atom_per_sys = n_atom

            if max(atom_type_num.values()) > max_n_atom_per_type:
                max_n_atom_per_type = max(atom_type_num.values())

            if self.ref_energy is None:
                self.ref_energy = row.data.get("ref_energy", None)
            if self.mass is None:
                self.mass = row.data.get("mass", None)

        # Set header data
        header_data["n_conf"] = conf_num
        header_data["max_n_atom_type"] = max_n_atom_type
        header_data["all_atom_type"] = all_atom_type
        header_data["max_n_atom_per_sys"] = max_n_atom_per_sys
        header_data["max_n_atom_per_type"] = max_n_atom_per_type

        if self.ref_energy is None:
            self.ref_energy = []
            for _ in range(max_n_atom_type):
                self.ref_energy.append(0.0)
        header_data["ref_energy"] = self.ref_energy

        if self.mass is None:
            self.mass = []
            for element in all_atom_type:
                an = atomic_numbers[element]
                self.mass.append(atomic_masses[an])
        header_data["mass"] = self.mass

        header_data["n_basis"] = n_basis

        for basis_tag in all_basis.keys():
            header_data[basis_tag] = all_basis[basis_tag]

        return header_data, training_data
