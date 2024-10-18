class Abn:
    def __init__(self, ml_abn):
        self.ml_abn = ml_abn

    def read(self):
        header_data = {}
        configurations = []
        current_config = None
        in_header = True

        with open(self.ml_abn, 'r') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if line.startswith("Configuration num."):
                in_header = False
                if current_config:
                    configurations.append(current_config)
                current_config = {"configuration_num": line.split()[-1]}
            elif in_header:
                if line.startswith("The number of configurations"):
                    header_data["number_of_configurations"] = int(lines[lines.index(line) + 1].strip())
                elif line.startswith("The maximum number of atom type"):
                    header_data["max_atom_type"] = int(lines[lines.index(line) + 1].strip())
                elif line.startswith("The atom types in the data file"):
                    header_data["atom_types"] = lines[lines.index(line) + 1].strip().split()
                elif line.startswith("The maximum number of atoms per system"):
                    header_data["max_atoms_per_system"] = int(lines[lines.index(line) + 1].strip())
                elif line.startswith("The maximum number of atoms per atom type"):
                    header_data["max_atoms_per_atom_type"] = int(lines[lines.index(line) + 1].strip())
                elif line.startswith("Reference atomic energy (eV)"):
                    header_data["reference_atomic_energy"] = list(map(float, lines[lines.index(line) + 1].strip().split()))
                elif line.startswith("Atomic mass"):
                    header_data["atomic_mass"] = list(map(float, lines[lines.index(line) + 1].strip().split()))
                elif line.startswith("The numbers of basis sets per atom type"):
                    header_data["basis_sets_per_atom_type"] = list(map(int, lines[lines.index(line) + 1].strip().split()))
                elif line.startswith("Basis set for Ce"):
                    header_data["basis_set_Ce"] = []
                    for i in range(13):
                        header_data["basis_set_Ce"].append(list(map(int, lines[lines.index(line) + 1 + i].strip().split())))
                elif line.startswith("Basis set for O"):
                    header_data["basis_set_O"] = []
                    for i in range(19):
                        header_data["basis_set_O"].append(list(map(int, lines[lines.index(line) + 1 + i].strip().split())))
            else:
                if line.startswith("System name"):
                    current_config["system_name"] = lines[lines.index(line) + 1].strip()
                elif line.startswith("The number of atom types"):
                    current_config["num_atom_types"] = int(lines[lines.index(line) + 1].strip())
                elif line.startswith("The number of atoms"):
                    current_config["num_atoms"] = int(lines[lines.index(line) + 1].strip())
                elif line.startswith("Atom types and atom numbers"):
                    current_config["atom_types_numbers"] = {}
                    current_config["atom_types_numbers"]["Ce"] = int(lines[lines.index(line) + 1].strip().split()[1])
                    current_config["atom_types_numbers"]["O"] = int(lines[lines.index(line) + 2].strip().split()[1])
                elif line.startswith("CTIFOR"):
                    current_config["ctifor"] = float(lines[lines.index(line) + 1].strip())
                elif line.startswith("Primitive lattice vectors (ang.)"):
                    current_config["lattice_vectors"] = []
                    for i in range(3):
                        current_config["lattice_vectors"].append(list(map(float, lines[lines.index(line) + 1 + i].strip().split())))
                elif line.startswith("Atomic positions (ang.)"):
                    current_config["atomic_positions"] = []
                    for i in range(current_config["num_atoms"]):
                        current_config["atomic_positions"].append(list(map(float, lines[lines.index(line) + 1 + i].strip().split())))
                elif line.startswith("Total energy (eV)"):
                    current_config["total_energy"] = float(lines[lines.index(line) + 1].strip())
                elif line.startswith("Forces (eV ang.^-1)"):
                    current_config["forces"] = []
                    for i in range(current_config["num_atoms"]):
                        current_config["forces"].append(list(map(float, lines[lines.index(line) + 1 + i].strip().split())))
                elif line.startswith("Stress (kbar)"):
                    current_config["stress"] = {}
                    current_config["stress"]["XX_YY_ZZ"] = list(map(float, lines[lines.index(line) + 2].strip().split()))
                    current_config["stress"]["XY_YZ_ZX"] = list(map(float, lines[lines.index(line) + 4].strip().split()))

        if current_config:
            configurations.append(current_config)

        return {"header": header_data, "configurations": configurations}
