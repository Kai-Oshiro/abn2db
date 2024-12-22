
class Outcar:
    def __init__(self):
        self.n_atom_tag = "NIONS"
        self.ionic_step_tag = "Ionic step"
        self.lattice_tag = "direct lattice vectors"
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
        entire_data = []
        for idx, line in enumerate(lines):
            if self.n_atom_tag in line:
                n_atom = int(line.split()[-1])

            if self.ionic_step_tag in line:
                self.start_ionic_step = True

            if self.start_ionic_step:
                if self.ionic_step_tag in line:
                    ionic_step = int(line.split()[-2])
                    step_results = {"ionic_step": ionic_step}
                    step_results["n_atom"] = n_atom

                if self.lattice_tag in line:
                    lattice = []
                    for i in range(3):
                        lattice.append([float(x) for x in lines[idx+i+1].split()[0:3]])
                    step_results["lattice"] = lattice

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

                    entire_data.append(step_results)



        return entire_data
