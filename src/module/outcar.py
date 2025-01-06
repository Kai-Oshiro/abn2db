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
                    step_results = {"ionic_step": ionic_step}
                    step_results["atom_type"] = atom_type
                    step_results["n_atom"] = n_atom
                    step_results["n_atom_per_type"] = n_atom_per_type
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
