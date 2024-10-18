class Abn:
    def __init__(self, ml_abn):
        self.ml_abn = ml_abn
        self.star_line = "**************************************************"
        self.dash_line = "--------------------------------------------------"
        self.eq_line = "=================================================="

        # Flags for the header data
        self.n_conf_flag = "The number of configurations"
        self.max_n_atom_type_flag = "The maximum number of atom type"
        self.all_atom_type_flag = "The atom types in the data file"
        self.max_n_atom_per_sys_flag = "The maximum number of atoms per system"
        self.max_n_atom_per_type_flag = "The maximum number of atoms per atom type"
        self.ref_ene_flag = "Reference atomic energy (eV)"
        self.mass_flag = "Atomic mass"
        self.n_basis_flag = "The numbers of basis sets per atom type"
        self.basis_flag = "Basis set for"

        # Flags for the training data
        self.conf_flag = "Configuration num."
        self.sys_name_flag = "System name"
        self.n_atom_flag = "The number of atom types"
        self.n_atom = "The number of atoms"
        self.atom_type_flag = "Atom types and atom numbers"
        self.ctifor_flag = "CTIFOR"
        self.vec_flag = "Primitive lattice vectors (ang.)"
        self.pos_flag = "Atomic positions (ang.)"
        self.ene_flag = "Total energy (eV)"
        self.force_flag = "Forces (eV ang.^-1)"
        self.stress_flag = "Stress (kbar)"

    def get_section_end_idx(self, lines, start_idx, flag):
        end_idx = -1
        for i, line in enumerate(lines[start_idx:], start=start_idx):
            if line.startswith(flag):
                end_idx = i
                break
        return end_idx

    def read_file(self):
        is_header = True
        header_data = {}
        training_data = []

        with open(self.ml_abn, 'r') as file:
            lines = file.readlines()

        header_data["version"] = lines[0].strip()
        print(header_data["version"])

        for i, line in enumerate(lines):
            if line.startswith(self.star_line):

                if self.n_conf_flag in lines[i+1]:
                    header_data["n_conf"] = int(lines[i+3].strip())
                    print(f"n_conf: {header_data['n_conf']}")

                elif self.max_n_atom_type_flag in lines[i+1]:
                    header_data["max_n_atom_type"] = int(lines[i+3].strip())
                    print(f"max_n_atom_type: {header_data['max_n_atom_type']}")

                elif self.all_atom_type_flag in lines[i+1]:
                    end_idx = self.get_section_end_idx(lines, i+1, self.star_line)
                    all_atom_type = []
                    for j in range(i+3, end_idx):
                        #print(lines[j].strip().split())
                        all_atom_type.extend(lines[j].strip().split())
                    header_data["all_atom_type"] = all_atom_type
                    print(f"all_atom_type: {header_data['all_atom_type']}")

                elif self.max_n_atom_per_sys_flag in lines[i+1]:
                    header_data["max_n_atom_per_sys"] = int(lines[i+3].strip())
                    print(f"max_n_atom_per_sys: {header_data['max_n_atom_per_sys']}")

                elif self.max_n_atom_per_type_flag in lines[i+1]:
                    header_data["max_n_atom_per_type"] = int(lines[i+3].strip())
                    print(f"max_n_atom_per_type: {header_data['max_n_atom_per_type']}")

                elif self.ref_ene_flag in lines[i+1]:
                    end_idx = self.get_section_end_idx(lines, i+1, self.star_line)
                    ref_ene = []
                    for j in range(i+3, end_idx):
                        ref_ene.extend([float(x) for x in lines[j].strip().split()])
                    header_data["ref_ene"] = ref_ene
                    print(f"ref_ene: {header_data['ref_ene']}")

                elif self.mass_flag in lines[i+1]:
                    end_idx = self.get_section_end_idx(lines, i+1, self.star_line)
                    mass = []
                    for j in range(i+3, end_idx):
                        mass.extend([float(x) for x in lines[j].strip().split()])
                    header_data["mass"] = mass
                    print(f"mass: {header_data['mass']}")

                elif self.n_basis_flag in lines[i+1]:
                    end_idx = self.get_section_end_idx(lines, i+1, self.star_line)
                    n_basis = []
                    for j in range(i+3, end_idx):
                        n_basis.extend([int(x) for x in lines[j].strip().split()])
                    header_data["n_basis"] = n_basis
                    print(f"n_basis: {header_data['n_basis']}")

                elif self.basis_flag in lines[i+1]:
                    end_idx = self.get_section_end_idx(lines, i+1, self.star_line)
                    basis = {}
                    atom_type = lines[i+1].split()[-1]
                    for j in range(i+3, end_idx):
                        config_idx, atom_idx = map(int, lines[j].split())
                        if config_idx not in basis:
                            basis[config_idx] = []
                        basis[config_idx].append(atom_idx)
                    header_data[f"basis_for_{atom_type}"] = basis
                    print(f"basis_for_{atom_type}: {header_data[f'basis_for_{atom_type}']}")

                elif self.conf_flag in lines[i+1]:
                    is_header = False
                    conf_section_idx = i - 1
                    break

        for i, line in enumerate(lines[conf_section_idx:], start=conf_section_idx):
            if line.startswith(self.star_line):
                if self.conf_flag in lines[i+1]:
                    config_data = {}
                    config_data["conf_num"] = int(lines[i+1].strip().split()[-1])
                    for j, config_header_line in enumerate(lines[i+2:], start=i+2):
                        if self.sys_name_flag in config_header_line:
                            config_data["sys_name"] = config_header_line.strip()
                            print(f"sys_name: {config_data['sys_name']}")
                        elif self.n_atom_flag in config_header_line:
                            config_data["n_atom_type"] = int(lines[j+2].strip())
                            print(f"n_atom_type: {config_data['n_atom_type']}")
                        elif self.n_atom in config_header_line:
                            config_data["n_atom"] = int(lines[j+2].strip())
                            print(f"n_atom: {config_data['n_atom']}")
                            break
                elif self.atom_type_flag in lines[i+1]:
                    atom_type_num = {}
                    for j in range(i+3, i+3+config_data["n_atom_type"]):
                        atom, num = lines[j].strip().split()
                        atom_type_num[atom] = int(num)
                    config_data["atom_type_num"] = atom_type_num
                    print(f"atom_type_num: {config_data['atom_type_num']}")

                    training_data.append(config_data)

        #return {"header_data": header_data, "training_data": training_data}
