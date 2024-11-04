import os

from ase import Atoms
from ase.calculators.singlepoint import SinglePointDFTCalculator
from ase.db import connect

class Database:
    def __init__(self):
        self.cwd = os.getcwd()

    def _make_db(self):
        db_path = os.path.join(self.cwd, self.file_name + ".db")
        if os.path.exists(db_path):
            raise FileExistsError(f"{db_path} already exists.")

        db = connect(db_path)

        return db

    def write_db(self, header_data, training_data, file_name):
        self.header_data = header_data
        self.training_data = training_data
        self.file_name = file_name

        db = self._make_db()

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
                conf_num=conf_num,
                ctifor=ctifor,
                data={"basis": basis}
                )
