import os
import re

class Outcar:
    def __init__(self):
        # Keywords for common parameters
        self.atom_type_tag = "VRHFIN"
        self.mass_tag = "mass and valenz"
        self.n_atom_tag = "NIONS"
        self.n_atom_per_type_tag = "ions per type ="
        self.system_tag = "POSCAR ="

        # Keywords for DFT and MLFF sections
        self.dft_section_flag = "FORCE on cell =-STRESS in cart. coord.  units (eV):"
        self.mlff_section_flag = "ML FORCE on cell =-STRESS in cart. coord. units (eV/cell)"

        # Keywords for DFT and MLFF results
        self.ionic_step_tag = "Ionic step"
        self.stress_tag = "in kB"
        self.vectors_tag = "direct lattice vectors"
        self.position_tag = "POSITION"
        self.force_tag = "TOTAL-FORCE (eV/Angst)"
        self.free_energy_tag = "free  energy" # Handle both MLFF and DFT energies
        self.energy_tag = "energy  without entropy="

    def load(self, outcar_path):
        """
        Extract computational results from OUTCAR file.

        Parameters
        ----------
        outcar_path : str
            Path to OUTCAR file to be loaded.

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
                    "free_energy": -1234.5678,
                    "energy": -1234.5678,
                    "is_dft": True,
                },
                ...
            ]
            "stress" contains elements in the order XX, YY, ZZ, XY, YZ, ZX.
        """

        with open(outcar_path, 'r') as f:
            lines = f.readlines()


        # Initialize common parameters
        file_name = os.path.basename(outcar_path)
        common_data = {"file_name": file_name}
        element_list = []
        mass = []

        ### Get common parameters ###
        for line in lines:
            if self.atom_type_tag in line:
                match = re.search(r"=(.*?):", line)
                if match:
                    element_list.append(match.group(1).strip())

            if self.mass_tag in line:
                mass_line = line.split(";")[0].replace("POMASS =", "").strip()
                mass.append(float(mass_line))

            if self.n_atom_tag in line:
                n_atom = int(line.split()[-1])

            if self.n_atom_per_type_tag in line:
                n_atom_per_type = list(map(int, line.split("=")[1].split()))
                # Check if the length of element_list (POTCAR-derived?) and n_atom_per_type (POSCAR-derived?) match
                if len(element_list) != len(n_atom_per_type):
                    raise ValueError("Mismatch between element list and atom per type list.")
                n_atom_type = len(element_list)
                atom_type_num = dict(zip(element_list, n_atom_per_type))

            if self.system_tag in line:
                sys_name = line.replace(self.system_tag, "").strip()
                break # Exit the loop once all common parameters are found

        # Add common parameters to the dictionary
        common_data["mass"] = mass
        common_data["n_atom"] = n_atom
        common_data["n_atom_type"] = n_atom_type
        common_data["atom_type_num"] = atom_type_num
        common_data["sys_name"] = sys_name

        # Initialize ionic step data
        outcar_data = []
        is_dft = False
        is_step = False

        ### Get results from ionic step ###
        for idx, line in enumerate(lines):
            # Skip extra “direct lattice vectors” 
            # keyword at the beginning of OUTCAR.
            if self.ionic_step_tag in line:
                ionic_step = int(line.split()[-2])
                is_step = True
            # Skip header section until the first ionic step
            if not is_step:
                continue

            # Judge if the current section is DFT or MLFF
            if self.dft_section_flag in line:
                is_dft = True
            if self.mlff_section_flag in line:
                is_dft = False

            # Get computational results
            if self.stress_tag in line:
                stress = [float(x) for x in line.split()[2:8]]

            if self.vectors_tag in line:
                vectors = []
                for i in range(3):
                    vectors.append([float(x) for x in lines[idx+i+1].split()[0:3]])

            if self.position_tag in line:
                positions = []
                forces = []
                for i in range(n_atom):
                    positions.append([float(x) for x in lines[idx+i+2].split()[0:3]])
                    forces.append([float(x) for x in lines[idx+i+2].split()[3:6]])

            if self.free_energy_tag in line:
                if is_dft:
                    free_energy = float(line.split()[4])
                else:
                    free_energy = float(line.split()[5])

            if self.energy_tag in line:
                if is_dft:
                    energy = float(line.split()[3])
                else:
                    energy = float(line.split()[4])

                step_data = {"ionic_step": ionic_step}
                step_data.update(common_data)
                step_data["is_dft"] = is_dft
                step_data["stress"] = stress
                step_data["vectors"] = vectors
                step_data["positions"] = positions
                step_data["forces"] = forces
                step_data["free_energy"] = free_energy
                step_data["energy"] = energy

                outcar_data.append(step_data)

        return outcar_data



    def filter_data(self, outcar_data, data_type):
        """
        Filter OUTCAR data based on the specified data type (DFT, MLFF, or both).

        Parameters
        ----------
        outcar_data : list
            A list of dictionaries containing OUTCAR data.
        data_type : str
            Type of data to extract (e.g., 'dft', 'mlff', 'both').

        Returns
        -------
        filtered_outcar_data : list
            A list of dictionaries containing filtered OUTCAR data.
        """

        data_type = data_type.lower()
        if data_type.startswith("b"):
            return outcar_data

        filtered_outcar_data = []
        is_dft_required = False
        if data_type.startswith("d"):
            is_dft_required = True

        for data in outcar_data:
            if data["is_dft"] == is_dft_required:
                filtered_outcar_data.append(data)

        return filtered_outcar_data



    def _find_atom_by_index(self, atom_type_num, index):
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
        Extract header and training data from OUTCAR data.

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
                    "free_energy": -1234.5678,
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
                    "free_energy": -1234.5678,
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
                    element = self._find_atom_by_index(step_results["atom_type_num"], i)
                    if element in basis:
                        basis[element].append(i)
                    else:
                        basis[element] = [i]
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
            data["free_energy"] = step_results["free_energy"]
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

