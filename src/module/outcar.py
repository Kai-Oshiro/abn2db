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



    def parse_data(self, outcar_data):
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
        for data in outcar_data:
            # Extract header data
            if data["n_atom_type"] > max_n_atom_type:
                max_n_atom_type = data["n_atom_type"]

            for index, (atom_type, n_atom_per_type) in enumerate(data["atom_type_num"].items()):
                if atom_type not in all_atom_type:
                    all_atom_type.append(atom_type)

                    ref_energy.append(0.0)

                if n_atom_per_type > max_n_atom_per_type:
                    max_n_atom_per_type = n_atom_per_type

                if data["mass"][index] not in mass:
                    mass.append(data["mass"][index])

            # Add n_basis related process

            if data["n_atom"] > max_n_atom_per_sys:
                max_n_atom_per_sys = data["n_atom"]

            header_data["max_n_atom_type"] = max_n_atom_type
            header_data["all_atom_type"] = all_atom_type
            header_data["max_n_atom_per_sys"] = max_n_atom_per_sys
            header_data["max_n_atom_per_type"] = max_n_atom_per_type
            header_data["ref_energy"] = ref_energy
            header_data["mass"] = mass
            header_data["n_basis"] = n_basis

            # Extract training data
            result_dict = {"conf_num": count}
            result_dict["sys_name"] = data["sys_name"]
            result_dict["n_atom_type"] = data["n_atom_type"]
            result_dict["n_atom"] = data["n_atom"]
            result_dict["atom_type_num"] = data["atom_type_num"]
            result_dict["ctifor"] = 0.002
            result_dict["vectors"] = data["vectors"]
            result_dict["positions"] = data["positions"]
            result_dict["energy"] = data["energy"]
            result_dict["forces"] = data["forces"]
            result_dict["stress"] = data["stress"]

            training_data.append(result_dict)

            count += 1

        return header_data, training_data

