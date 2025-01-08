import os
import re

class Outcar:
    def __init__(self):
        self.atom_type_tag = "VRHFIN"
        self.n_atom_tag = "NIONS"
        self.n_atom_per_type_tag = "ions per type ="
        self.system_tag = "POSCAR ="
        self.mass_tag = "Mass of Ions in am"
        self.ionic_step_tag = "Ionic step"
        self.vectors_tag = "direct lattice vectors"
        self.position_tag = "POSITION"
        self.force_tag = "TOTAL-FORCE (eV/Angst)"
        self.energy_tag = "free  energy   TOTEN  ="
        self.stress_tag = "in kB"

    def read_outcar(self, outcar_path):
        """
        Read OUTCAR file
        """

        file_name = os.path.basename(outcar_path)

        with open(outcar_path, 'r') as f:
            lines = f.readlines()

        self.start_ionic_step = False
        outcar_data = []
        atom_type = []
        for idx, line in enumerate(lines):
            if self.atom_type_tag in line:
                match = re.search(r"=(.*?):", line)
                atom_type.append(match.group(1))

            if self.n_atom_tag in line:
                n_atom = int(line.split()[-1])

            if self.n_atom_per_type_tag in line:
                n_atom_per_type = list(map(int, line.split("=")[1].split()))

                if len(atom_type) != len(n_atom_per_type):
                    raise ValueError("Number of atom types and number of atoms per type do not match.")
                else:
                    n_atom_type = len(atom_type)
                    atom_type_num = dict(zip(atom_type, n_atom_per_type))

            if self.system_tag in line:
                sys_name = line.split()[-1]

            if self.mass_tag in line:
                mass_line = lines[idx+1].split()
                mass = [float(x) for x in mass_line[2:]]

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



def find_atom_by_index(atom_type_num, index):
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
    atom_type : str
        The atom name corresponding to the given index.

    Raises
    ------
    ValueError
        If the index is out of range.
    """
    current_index = 1
    for atom_type, count in atom_type_num.items():
        if current_index <= index < current_index + count:
            return atom_type
        current_index += count
    raise ValueError(f"Index {index} is out of range")

    def parse_data(self, outcar_data, raw_basis):
        """
        Parse OUTCAR data
        """

        header_data = {}
        training_data = []

        count = 1
        max_n_atom_type = 0
        all_atom_type = []
        max_n_atom_per_sys = 0
        max_n_atom_per_type = 0
        ref_energy = []
        mass = []
        n_basis = []
        for step_results in outcar_data:
            # Extract header data
            if step_results["n_atom_type"] > max_n_atom_type:
                max_n_atom_type = step_results["n_atom_type"]

            for index, (atom_type, n_atom_per_type) in enumerate(step_results["atom_type_num"].items()):
                if atom_type not in all_atom_type:
                    all_atom_type.append(atom_type)

                    ref_energy.append(0.0)

                if n_atom_per_type > max_n_atom_per_type:
                    max_n_atom_per_type = n_atom_per_type

                if step_results["mass"][index] not in mass:
                    mass.append(step_results["mass"][index])

            # Add n_basis related process
            basis = {} # {atom_type: [indices]}
            if raw_basis:
                for i in raw_basis:
                    atom_type = find_atom_by_index(step_results["atom_type_num"], i)
                    if atom_type in basis:
                        basis[atom_type].append(i)
                    else:
                        basis[atom_type] = [i]

            ### Obtain n_basis, basis_for_X data ###

            if step_results["n_atom"] > max_n_atom_per_sys:
                max_n_atom_per_sys = step_results["n_atom"]

            # Extract training data
            data = {"conf_num": count}
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

            count += 1

        header_data["max_n_atom_type"] = max_n_atom_type
        header_data["all_atom_type"] = all_atom_type
        header_data["max_n_atom_per_sys"] = max_n_atom_per_sys
        header_data["max_n_atom_per_type"] = max_n_atom_per_type
        header_data["ref_energy"] = ref_energy
        header_data["mass"] = mass
        header_data["n_basis"] = n_basis

        return header_data, training_data

