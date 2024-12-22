import os
import numpy as np

from ase import Atoms
from ase.calculators.singlepoint import SinglePointDFTCalculator
from ase.db import connect
from ase.data import atomic_numbers, atomic_masses

class Database:
    def __init__(self):
        self.cwd = os.getcwd()

    def write_db(self, header_data, training_data, db_path):
        self.header_data = header_data
        self.training_data = training_data

        db = connect(db_path)

        ref_energy = self.header_data["ref_energy"]
        mass = self.header_data["mass"]
        for result_dict in self.training_data:
            unique_species = list(result_dict["atom_type_num"].keys())
            species = [key for key, count in result_dict["atom_type_num"].items() for _ in range(count)]
            vectors = result_dict["vectors"]
            positions = result_dict["positions"]

            atoms = Atoms(
                species,
                cell=vectors,
                positions=positions,
                pbc=True
                )

            free_energy = result_dict["energy"]
            forces = result_dict["forces"]
            stress = result_dict["stress"]

            calculator = SinglePointDFTCalculator(
                atoms,
                free_energy=free_energy,
                forces=forces,
                stress=stress
                )

            atoms.set_calculator(calculator)
            atoms.calc.name = "vasp"

            sys_name = str(result_dict["sys_name"])
            conf_num = int(result_dict["conf_num"])
            ctifor = float(result_dict["ctifor"])

            basis = {}
            for element in unique_species:
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

    def read_db(self, db_path, ref_energy=None, mass=None):
        self.db_path = db_path
        self.ref_energy = ref_energy
        self.mass = mass

        db = connect(self.db_path)

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
            species = atoms.get_chemical_symbols()
            n_atom_type = len(set(species))
            n_atom = len(species)
            #print(f"conf_num: {conf_num}, sys_name: {sys_name}, n_atom_type: {n_atom_type}, n_atom: {n_atom}")

            atom_type_num = {}
            for element in species:
                if element in atom_type_num:
                    atom_type_num[element] += 1
                else:
                    atom_type_num[element] = 1
            #print(f"atom_type_num: {atom_type_num}")

            try:
                ctifor = row.ctifor
            except:
                ctifor = 0.002 # Default value of ML_CTIFOR in VASP

            try:
                basis = row.data.basis # Dictionary; {element: [basis]}
            except:
                basis = {}
                for element in atom_type_num.keys():
                    basis[element] = []
            #print(f"basis: {basis}")

            vectors = row.cell.tolist()
            positions = row.positions.tolist()
            # The "energy" in the ML_ABN file corresponds to the "free energy" in the OUTCAR file, 
            # so it is registered as "free energy" in the atoms object.
            # On the other hand, variables and keys conform to the ML_ABN file 
            # and are represented as "energy".
            energy = row.free_energy
            forces = row.forces.tolist()
            stress = row.stress.tolist()

            training_data.append({
                "conf_num": conf_num,
                "sys_name": sys_name,
                "ctifor": ctifor,
                "atom_type_num": atom_type_num,
                "vectors": vectors,
                "positions": positions,
                "energy": energy,
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
        #print(f"n_basis: {n_basis}")

        for basis_tag in all_basis.keys():
            header_data[basis_tag] = all_basis[basis_tag]

        return header_data, training_data
