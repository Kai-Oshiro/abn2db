import os
import re

class Outcar:
    def __init__(self):
        self.atom_type_tag = "VRHFIN"
        self.n_atom_tag = "NIONS"
        self.n_atom_per_type_tag = "ions per type ="
        self.system_tag = "POSCAR ="
        self.mass_tag = "mass and valenz"
        self.ionic_step_tag = "Ionic step"
        self.vectors_tag = "direct lattice vectors"
        self.position_tag = "POSITION"
        self.force_tag = "TOTAL-FORCE (eV/Angst)"
        self.energy_tag = "free  energy   TOTEN  ="
        self.stress_tag = "in kB"

    def read_outcar(self, outcar_path):
        """
        Read OUTCAR file

        Parameters
        ----------
        outcar_path : str
            The path to the OUTCAR file.

        Returns
        -------
        outcar_data : list
            A list of dictionaries containing OUTCAR data.
            Example: 
            [
                {
                    "file_name": "OUTCAR_00",
                    "ionic_step": 1,
                    "n_atom": 144,
                    "n_atom_type": 2,
                    "atom_type_num": {"Ce": 48, "O": 96},
                    "sys_name": "CeO2",
                    "mass": [140.115, 16.0],
                    "stress": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
                    "vectors": [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]],
                    "positions": [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], ...],
                    "forces": [[0.1, 0.2, 0.3], [-0.1, -0.2, -0.3], ...],
                    "energy": -1234.5678,
                },
                ...
            ]
            "stress" contains elements in the order XX, YY, ZZ, XY, YZ, ZX.
        """

        file_name = os.path.basename(outcar_path)

        with open(outcar_path, 'r') as f:
            lines = f.readlines()

        self.start_ionic_step = False
        outcar_data = []
        element_list = []
        mass = []
        for idx, line in enumerate(lines):
            if self.atom_type_tag in line:
                match = re.search(r"=(.*?):", line)
                element_list.append(match.group(1).strip())

            if self.n_atom_tag in line:
                n_atom = int(line.split()[-1])

            if self.n_atom_per_type_tag in line:
                n_atom_per_type = list(map(int, line.split("=")[1].split()))

                if len(element_list) != len(n_atom_per_type):
                    raise ValueError("Number of atom types and number of atoms per type do not match.")
                else:
                    n_atom_type = len(element_list)
                    atom_type_num = dict(zip(element_list, n_atom_per_type))

            if self.system_tag in line:
                sys_name = line.replace(self.system_tag, "").strip()

            if self.mass_tag in line:
                mass_line = lines[idx].split(";")[0]
                mass_line = mass_line.replace("POMASS =", "").strip()
                mass.append(float(mass_line))

            if self.ionic_step_tag in line:
                self.start_ionic_step = True

            if self.start_ionic_step:
                if self.ionic_step_tag in line:
                    ionic_step = int(line.split()[-2])
                    step_results = {"file_name": file_name}
                    step_results["ionic_step"] = ionic_step
                    step_results["n_atom"] = n_atom
                    step_results["n_atom_type"] = n_atom_type
                    step_results["atom_type_num"] = atom_type_num
                    step_results["sys_name"] = sys_name
                    step_results["mass"] = mass

                if self.vectors_tag in line:
                    vectors = []
                    for i in range(3):
                        vectors.append([float(x) for x in lines[idx+i+1].split()[0:3]])
                    step_results["vectors"] = vectors

                if self.position_tag in line:
                    positions = []
                    forces = []
                    for i in range(n_atom):
                        positions.append([float(x) for x in lines[idx+i+2].split()[0:3]])
                        forces.append([float(x) for x in lines[idx+i+2].split()[3:6]])
                    step_results["positions"] = positions
                    step_results["forces"] = forces

                if self.energy_tag in line:
                    energy = float(line.split()[4])
                    step_results["energy"] = energy

                if self.stress_tag in line:
                    stress = [float(x) for x in lines[idx].split()[2:8]]
                    step_results["stress"] = stress

                    outcar_data.append(step_results)

        return outcar_data



    def find_atom_by_index(self, atom_type_num, index):
        """
        Given an index, determine which atom it corresponds to.

        Parameters
        ----------
        atom_type_num : dict
            A dictionary containing atom names and their counts.
            Example: {"Ce": 8, "O": 16}
        index : int

        Returns
        -------
        element : str
            The atom name corresponding to the given index.

        Raises
        ------
        ValueError
            If the index is out of range.
        """
        current_index = 1
        for element, count in atom_type_num.items():
            if current_index <= index < current_index + count:
                return element
            current_index += count
        raise ValueError(f"Index {index} is out of range")

    def parse_data(self, outcar_data, raw_basis):
        """
        Parse OUTCAR data

        Parameters
        ----------
        outcar_data : list
            A list of dictionaries containing OUTCAR data.
            Example: 
            [
                {
                    "file_name": "OUTCAR_00",
                    "ionic_step": 1,
                    "n_atom": 144,
                    "n_atom_type": 2,
                    "atom_type_num": {"Ce": 48, "O": 96},
                    "sys_name": "CeO2",
                    "mass": [140.115, 16.0],
                    "stress": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6],
                    "vectors": [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]],
                    "positions": [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], ...],
                    "forces": [[0.1, 0.2, 0.3], [-0.1, -0.2, -0.3], ...],
                    "energy": -1234.5678,
                },
                ...
            ]
            "stress" contains elements in the order XX, YY, ZZ, XY, YZ, ZX.

        raw_basis : list
            A list of atom indices for the basis set of training data.
            Example: [1, 3, 5]

        Returns
        -------
        header_data : dict
            A dictionary containing header data.
            Example:
            {
                "n_conf": 1,
                "max_n_atom_type": 2,
                "all_atom_type": ["Ce", "O"],
                "max_n_atom_per_sys": 144,
                "max_n_atom_per_type": 96,
                "ref_energy": [0.0, 0.0],
                "mass": [140.115, 16.0],
                "n_basis": {'Ce': 1, 'O': 1},
                "basis_for_Ce": {1: [1]},
                "basis_for_O": {1: [1]}
            }

        training_data : list
            A list of dictionaries containing training data.
            Example:
            [
                {
                    "conf_num": 1,
                    "sys_name": "CeO2",
                    "n_atom_type": 2,
                    "n_atom": 144,
                    "atom_type_num": {"Ce": 48, "O": 96},
                    "ctifor": 0.002,
                    "vectors": [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]],
                    "positions": [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], ...],
                    "energy": -1234.5678,
                    "forces": [[0.1, 0.2, 0.3], [-0.1, -0.2, -0.3], ...],
                    "stress": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
                },
                ...
            ]

        """

        header_data = {}
        training_data = []

        conf_num = 1
        max_n_atom_type = 0
        all_atom_type = []
        max_n_atom_per_sys = 0
        max_n_atom_per_type = 0
        ref_energy = []
        mass = []
        n_basis = {}
        all_basis = {}
        for step_results in outcar_data:
            # Extract header data
            if step_results["n_atom_type"] > max_n_atom_type:
                max_n_atom_type = step_results["n_atom_type"]

            # Add n_basis related process
            basis = {} # {element: [indices]}
            if raw_basis:
                for i in raw_basis:
                    element = self.find_atom_by_index(step_results["atom_type_num"], i)
                    if element in basis:
                        basis[element].append(i)
                    else:
                        basis[element] = [i]
                print(f"basis: {basis}")
            else:
                for element in step_results["atom_type_num"].keys():
                    basis[element] = []

            for index, (element, n_atom_per_type) in enumerate(step_results["atom_type_num"].items()):
                if element not in all_atom_type:
                    all_atom_type.append(element)

                    ref_energy.append(0.0)

                if n_atom_per_type > max_n_atom_per_type:
                    max_n_atom_per_type = n_atom_per_type

                if step_results["mass"][index] not in mass:
                    mass.append(step_results["mass"][index])

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

            if step_results["n_atom"] > max_n_atom_per_sys:
                max_n_atom_per_sys = step_results["n_atom"]

            # Extract training data
            data = {"conf_num": conf_num}
            data["sys_name"] = step_results["sys_name"]
            data["n_atom_type"] = step_results["n_atom_type"]
            data["n_atom"] = step_results["n_atom"]
            data["atom_type_num"] = step_results["atom_type_num"]
            data["ctifor"] = 0.002
            data["vectors"] = step_results["vectors"]
            data["positions"] = step_results["positions"]
            data["energy"] = step_results["energy"]
            data["forces"] = step_results["forces"]
            data["stress"] = step_results["stress"]

            training_data.append(data)

            conf_num += 1

        # Set header data
        header_data["n_conf"] = conf_num - 1
        header_data["max_n_atom_type"] = max_n_atom_type
        header_data["all_atom_type"] = all_atom_type
        header_data["max_n_atom_per_sys"] = max_n_atom_per_sys
        header_data["max_n_atom_per_type"] = max_n_atom_per_type
        header_data["ref_energy"] = ref_energy
        header_data["mass"] = mass
        header_data["n_basis"] = n_basis

        for basis_tag in all_basis.keys():
            header_data[basis_tag] = all_basis[basis_tag]

        return header_data, training_data

