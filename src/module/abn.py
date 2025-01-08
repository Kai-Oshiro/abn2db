import copy

class Abn:
    def __init__(self):
        self.star_line = "**************************************************"
        self.dash_line = "--------------------------------------------------"
        self.eq_line = "=================================================="

        # Flags for the header data
        self.n_conf_flag = "The number of configurations"
        self.max_n_atom_type_flag = "The maximum number of atom type"
        self.all_atom_type_flag = "The atom types in the data file"
        self.max_n_atom_per_sys_flag = "The maximum number of atoms per system"
        self.max_n_atom_per_type_flag = "The maximum number of atoms per atom type"
        self.ref_energy_flag = "Reference atomic energy (eV)"
        self.mass_flag = "Atomic mass"
        self.n_basis_flag = "The numbers of basis sets per atom type"
        self.basis_flag = "Basis set for"

        # Flags for the training data
        self.conf_flag = "Configuration num."
        self.sys_name_flag = "System name"
        self.n_atom_type_flag = "The number of atom types"
        self.n_atom_flag = "The number of atoms"
        self.atom_type_flag = "Atom types and atom numbers"
        self.ctifor_flag = "CTIFOR"
        self.vec_flag = "Primitive lattice vectors (ang.)"
        self.pos_flag = "Atomic positions (ang.)"
        self.energy_flag = "Total energy (eV)"
        self.force_flag = "Forces (eV ang.^-1)"
        self.stress_flag = "Stress (kbar)"

    # Helper functions for reading the ML_ABN file
    def _get_section_end_idx(self, lines, start_idx, end_flag):
        """
        Get the ending index of a section in the ML_ABN file.

        Parameters
        ----------
        lines : list
            List of lines from the loaded file
        start_idx : int
            Starting index of the section
        end_flag : str
            Flag to identify the end of the section

        Returns
        -------
        end_idx : int
            Ending index of the section
        """
        end_idx = -1
        for i, line in enumerate(lines[start_idx:], start=start_idx):
            if line.startswith(end_flag):
                end_idx = i
                break
        return end_idx

    def read_abn(self, abn_path):
        """
        Read the ABN file and extract relevant data.

        Parameters
        ----------
        abn_path : str
            Path to the ABN file to be read.

        Returns
        -------
        header_data : dict
            A dictionary containing header information.
            Example:
            {
                "n_conf": 100,
                "max_n_atom_type": 2,
                "all_atom_type": ["Ce", "O"],
                "max_n_atom_per_sys": 24,
                "max_n_atom_per_type": 16,
                "ref_energy": [0.0, 0.0],
                "mass": [140.115, 16.0],
                "n_basis": [1, 1],
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
                    "n_atom": 24,
                    "atom_type_num": {"Ce": 8, "O": 16},
                    "ctifor": 2.000000000000000E-003,
                    "vectors": [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]],
                    "positions": [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], ...],
                    "energy": -123.456,
                    "forces": [[0.1, 0.2, 0.3], [-0.1, -0.2, -0.3], ...],
                    "stress": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]    # [XX, YY, ZZ, XY, YZ, ZX]
                }
            ]
        """

        self.abn_path = abn_path

        header_data = {}
        training_data = []

        with open(self.abn_path, 'r') as file:
            lines = file.readlines()

        # Store file format version from the first line
        #header_data["version"] = lines[0].strip()

        """
        Read the header data.

        The header section of the ML_ABN file contains the following information:
        - The number of configurations
        - The maximum number of atom types
        - The atom types in the data file
        - The maximum number of atoms per system
        - The maximum number of atoms per atom type
        - Reference atomic energy (eV)
        - Atomic mass
        - The numbers of basis sets per atom type
        - Basis set for each atom type

        Each section is delimited by '***'.
        The title and content of each section are separated by '---'.

        Example:
        1.0 Version
        **************************************************
            Section title
        --------------------------------------------------
                Contents
        **************************************************
            ⋮
        **************************************************
            Section title
        --------------------------------------------------
                Contents
        **************************************************

        Loading of the header data will stop when the first 'Configuration num.' line is encountered.
        """

        ### Read the header data ###
        for i, line in enumerate(lines):
            # The number of configurations
            if self.n_conf_flag in line:
                header_data["n_conf"] = int(lines[i+2].strip())

            # The maximum number of atom types
            elif self.max_n_atom_type_flag in line:
                header_data["max_n_atom_type"] = int(lines[i+2].strip())

            # The atom types in the data file (single or multiple lines)
            elif self.all_atom_type_flag in line:
                end_idx = self._get_section_end_idx(lines, i, self.star_line)
                all_atom_type = []
                for j in range(i+2, end_idx):
                    all_atom_type.extend(lines[j].strip().split())
                header_data["all_atom_type"] = all_atom_type

            # The maximum number of atoms per system
            elif self.max_n_atom_per_sys_flag in line:
                header_data["max_n_atom_per_sys"] = int(lines[i+2].strip())

            # The maximum number of atoms per atom type
            elif self.max_n_atom_per_type_flag in line:
                header_data["max_n_atom_per_type"] = int(lines[i+2].strip())

            # Reference atomic energy (eV) (single or multiple lines)
            elif self.ref_energy_flag in line:
                end_idx = self._get_section_end_idx(lines, i, self.star_line)
                ref_energy = []
                for j in range(i+2, end_idx):
                    ref_energy.extend([float(x) for x in lines[j].strip().split()])
                header_data["ref_energy"] = ref_energy

            # Atomic mass (single or multiple lines)
            elif self.mass_flag in line:
                end_idx = self._get_section_end_idx(lines, i, self.star_line)
                mass = []
                for j in range(i+2, end_idx):
                    mass.extend([float(x) for x in lines[j].strip().split()])
                header_data["mass"] = mass

            # The numbers of basis sets per atom type (single or multiple lines)
            elif self.n_basis_flag in line:
                end_idx = self._get_section_end_idx(lines, i, self.star_line)
                basis_list = []
                for j in range(i+2, end_idx):
                    basis_list.extend([int(x) for x in lines[j].strip().split()])
                n_basis = {}
                for atom_type, n in zip(header_data["all_atom_type"], basis_list):
                    n_basis[atom_type] = n
                header_data["n_basis"] = n_basis

            # Basis set for each atom type (multiple lines)
            elif self.basis_flag in line:
                end_idx = self._get_section_end_idx(lines, i, self.star_line)
                basis = {}
                atom_type = lines[i].split()[-1]
                for j in range(i+2, end_idx):
                    config_idx, atom_idx = map(int, lines[j].split())
                    if config_idx not in basis:
                        basis[config_idx] = []
                    basis[config_idx].append(atom_idx)
                header_data[f"basis_for_{atom_type}"] = basis

            # Stop loading the header data 
            elif self.conf_flag in line:
                # Get the index of the last line of the header section
                conf_section_idx = i - 1
                break

        """
        Read the training data.
        
        The training data section of the ML_ABN file contains the following information:
        - Configuration num.
        - System name
        - The number of atom types
        - The number of atoms
        - Atom types and atom numbers
        - CTIFOR
        - Primitive lattice vectors (ang.)
        - Atomic positions (ang.)
        - Total energy (eV)
        - Forces (eV ang.^-1)
        - Stress (kbar)
        
        The training data consists of a summary of the structure and main data sections, 
        each separated by '***'.
        Each section is delimited by '==='.
        The title and content of each section are separated by '---'.

        Example:
        **************************************************
            Configuration num. int
        ==================================================
            System name
        --------------------------------------------------
                str
        ==================================================
            ⋮
        ==================================================
            The number of atoms
        --------------------------------------------------
                int
        **************************************************
            Atom types and atom numbers
        --------------------------------------------------
                str int (multiple lines)
        ==================================================
            ⋮
        ==================================================
            Stress (kbar)
        --------------------------------------------------
            XX YY ZZ
        --------------------------------------------------
        float float float
        --------------------------------------------------
            XY YZ ZX
        --------------------------------------------------
        float float float
        **************************************************
        """

        ### Read the training data ###
        for i, line in enumerate(lines[conf_section_idx:], start=conf_section_idx):
            # Configuration num.
            if self.conf_flag in line:
                result_dict = {} # Initialize the dictionary for each configuration data
                result_dict["conf_num"] = int(line.strip().split()[-1])

            # System name
            elif self.sys_name_flag in line:
                result_dict["sys_name"] = lines[i+2].strip()

            # The number of atom types
            elif self.n_atom_type_flag in line:
                #result_dict["n_atom_type"] = int(lines[i+2].strip())
                n_atom_type = int(lines[i+2].strip())

            # The number of atoms
            elif self.n_atom_flag in line:
                #result_dict["n_atom"] = int(lines[i+2].strip())
                n_atom = int(lines[i+2].strip())

            # Atom types and atom numbers (number of lines = n_atom_type)
            elif self.atom_type_flag in line:
                atom_type_num = {}
                for j in range(i+2, i+2+n_atom_type):
                    atom, num = lines[j].strip().split()
                    atom_type_num[atom] = int(num)
                result_dict["atom_type_num"] = atom_type_num

            # CTIFOR
            elif self.ctifor_flag in line:
                result_dict["ctifor"] = lines[i+2].strip()

            # Primitive lattice vectors (ang.) (3 * 3 matrix)
            elif self.vec_flag in line:
                vectors = []
                for j in range(i+2, i+5):
                    vectors.append([float(x) for x in lines[j].strip().split()])
                result_dict["vectors"] = vectors

            # Atomic positions (ang.) (n_atom * 3 matrix)
            elif self.pos_flag in line:
                positions = []
                for j in range(i+2, i+2+n_atom):
                    positions.append([float(x) for x in lines[j].strip().split()])
                result_dict["positions"] = positions

            # Total energy (eV)
            elif self.energy_flag in line:
                result_dict["energy"] = float(lines[i+2].strip())

            # Forces (eV ang.^-1) (n_atom * 3 matrix)
            elif self.force_flag in line:
                forces = []
                for j in range(i+2, i+2+n_atom):
                    forces.append([float(x) for x in lines[j].strip().split()])
                result_dict["forces"] = forces

            # Stress (kbar) (2 lines: diagonal and non-diagonal components)
            elif self.stress_flag in line:
                stress = []
                stress.extend([float(x) for x in lines[i+4].strip().split()])
                stress.extend([float(x) for x in lines[i+8].strip().split()])
                result_dict["stress"] = stress

                # Append the configuration data to the training data list
                training_data.append(copy.deepcopy(result_dict))

                # Continue to the next configuration data
                continue

        return header_data, training_data



    # Helper functions for writing the ML_ABN file
    # Following functions are designed to reproduce the ML_ABN file format generated by the VASP code.
    # They were created to verify changes from the original ML_ABN file using "diff" command.
    # It should not necessarily be required to use this notation...
    def _group_value(self, lst, group_size=3):
        """
        Group the values in a list.

        Parameters
        ----------
        lst : list
            List of values
        group_size : int
            Number of values to group

        Returns
        -------
        grouped_lst : list
            List of grouped values
        """
        return [lst[i:i+group_size] for i in range(0, len(lst), group_size)]

    def _get_width(self, value, part=None):
        """
        Get the width of a value.

        Parameters
        ----------
        value : float
            Value to get the width
        part : str
            Part of the value to get the width (int, float)
            int : Integer part of the value
            float : Decimal part of the value

        Returns
        -------
        _width : int
            Width of the value
        """
        value = abs(float(value))
        if part == "int":
            _width = len(str(int(value)))
        elif part == "float":
            _width = len(str(value).split(".")[1])
        else:
            _width = len(str(value))
        return _width

    def _get_max_width(self, lst, part=None):
        """
        Get the maximum width of a list of values.

        Parameters
        ----------
        lst : list
            List of values
        part : str
            Part of the value to get the width (int, float)

        Returns
        -------
        _max : int
            Maximum width of the values
        """
        if part == "int":
            _max = max([self._get_width(value, part="int") for value in lst])
        elif part == "float":
            _max = max([self._get_width(value, part="float") for value in lst])
        else:
            _max = max([self._get_width(value) for value in lst])
        return _max

    def _get_exp_notation(self, value, base_float_digits=14):
        """
        Get the value in exponential notation.

        Parameters
        ----------
        value : float
            Value to convert to exponential notation
        base_float_digits : int
            Number of digits for the floating point part

        Returns
        -------
        _str_line : str
            Value in exponential notation
        """
        if value == 0 or (isinstance(value, float) and abs(value) < 0.1):
            _str_line = f" {value:>22.15E}"
            # Indicate the exponential portion in 3 digits, default is 2 in Python
            if "E+" in _str_line:
                _str_line = _str_line.replace("E+", "E+0")
            elif "E-" in _str_line:
                _str_line = _str_line.replace("E-", "E-0")
        elif isinstance(value, float) and 0.1 <= abs(value) < 1:
            _str_line = f" {value:>18.15f}     "
        else:
            # Adjust to 16 digits overall
            int_width = self._get_width(value, part="int")
            float_digits = base_float_digits - int_width + 1
            _str_line = f" {value:>18.{float_digits}f}     "
        return _str_line

    def write_abn(self, header_data, training_data, db_path):
        """
        Write the header and training data to the ML_ABN file.

        Parameters
        ----------
        header_data : dict
            A dictionary containing header information.
            Example:
            {
                "n_conf": 100,
                "max_n_atom_type": 2,
                "all_atom_type": ["Ce", "O"],
                "max_n_atom_per_sys": 24,
                "max_n_atom_per_type": 16,
                "ref_energy": [0.0, 0.0],
                "mass": [140.115, 16.0],
                "n_basis": [1, 1],
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
                    "n_atom": 24,
                    "atom_type_num": {"Ce": 8, "O": 16},
                    "ctifor": 2.000000000000000E-003,
                    "vectors": [[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]],
                    "positions": [[0.0, 0.0, 0.0], [1.0, 1.0, 1.0], ...],
                    "energy": -123.456,
                    "forces": [[0.1, 0.2, 0.3], [-0.1, -0.2, -0.3], ...],
                    "stress": [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]    # [[XX YY ZZ], [XY YZ ZX]]
                }
            ]
        """
        lines = []
        space = "     "

        # Write the header data
        lines.append(" 1.0 Version")

        # The number of configurations
        lines.append(self.star_line)
        lines.append(f"{space}{self.n_conf_flag}")
        lines.append(self.dash_line)
        lines.append(f"{space}{header_data['n_conf']:>6}")

        # The maximum number of atom types
        lines.append(self.star_line)
        lines.append(f"{space}{self.max_n_atom_type_flag}")
        lines.append(self.dash_line)
        lines.append(f"{space}{header_data['max_n_atom_type']:>3}")

        # The atom types in the data file
        lines.append(self.star_line)
        lines.append(f"{space}{self.all_atom_type_flag}")
        lines.append(self.dash_line)

        grouped_all_atom_type = self._group_value(header_data["all_atom_type"])
        for atom_type_list in grouped_all_atom_type:
            content_line = f"{space}"
            for atom_type in atom_type_list:
                content_line += f"{atom_type:<2} "
            content_line = content_line.rstrip() # Remove the trailing space
            lines.append(content_line)

        # The maximum number of atoms per system
        lines.append(self.star_line)
        lines.append(f"{space}{self.max_n_atom_per_sys_flag}")
        lines.append(self.dash_line)
        lines.append(f"{space}{header_data['max_n_atom_per_sys']:>10}")

        # The maximum number of atoms per atom type
        lines.append(self.star_line)
        lines.append(f"{space}{self.max_n_atom_per_type_flag}")
        lines.append(self.dash_line)
        lines.append(f"{space}{header_data['max_n_atom_per_type']:>10}")

        # Reference atomic energy (eV)
        lines.append(self.star_line)
        lines.append(f"{space}{self.ref_energy_flag}")
        lines.append(self.dash_line)

        max_int_width = self._get_max_width(header_data["ref_energy"], part="int")
        grouped_ref_energy = self._group_value(header_data["ref_energy"])
        for energy_list in grouped_ref_energy:
            content_line = f""
            for energy in energy_list:
                str_line = self._get_exp_notation(energy)
                content_line += str_line
            lines.append(content_line)

        # Atomic mass
        lines.append(self.star_line)
        lines.append(f"{space}{self.mass_flag}")
        lines.append(self.dash_line)

        max_int_width = self._get_max_width(header_data["mass"], part="int")
        grouped_mass = self._group_value(header_data["mass"])
        for mass_list in grouped_mass:
            content_line = f""
            for mass in mass_list:
                str_line = self._get_exp_notation(mass)
                content_line += str_line
            lines.append(content_line)

        # The numbers of basis sets per atom type
        lines.append(self.star_line)
        lines.append(f"{space}{self.n_basis_flag}")
        lines.append(self.dash_line)

        n_basis = list(header_data["n_basis"].values())
        grouped_n_basis = self._group_value(n_basis)
        for n_basis_list in grouped_n_basis:
            content_line = f"{space}"
            for n_basis in n_basis_list:
                if n_basis == 0: # Handle the case where the basis set is not defined
                    n_basis = 1 # Set the dummy value
                content_line += f"{n_basis:>5} "
            content_line = content_line.rstrip()
            lines.append(content_line)

        # Basis set for each atom type
        for atom_type in header_data["all_atom_type"]:
            # Basis set for each atom type
            lines.append(self.star_line)
            lines.append(f"{space}{self.basis_flag} {atom_type:<2}")
            lines.append(self.dash_line)

            basis = header_data[f"basis_for_{atom_type}"]

            if not bool(basis): # Check if the basis (dictionary) is empty
                basis = {1: [1]} # Set the dummy key-value pair
            for conf_num, atom_idx_list in basis.items():
                for atom_idx in atom_idx_list:
                    content_line = f"{space}{conf_num:>6} {atom_idx:>6}"
                    lines.append(content_line)

        ### Write the training data ###
        for data in training_data:
            # Configuration num.
            lines.append(self.star_line)
            lines.append(f"{space}{self.conf_flag} {data['conf_num']:>6}")

            # System name
            lines.append(self.eq_line)
            lines.append(f"{space}{self.sys_name_flag}")
            lines.append(self.dash_line)
            lines.append(f"{space}{data['sys_name']:<40}")

            # Get atom info
            n_atom_type = len(data["atom_type_num"])
            n_atom = sum(data["atom_type_num"].values())

            # The number of atom types
            lines.append(self.eq_line)
            lines.append(f"{space}{self.n_atom_type_flag}")
            lines.append(self.dash_line)
            lines.append(f"{space}{n_atom_type:>3}")

            # The number of atoms
            lines.append(self.eq_line)
            lines.append(f"{space}{self.n_atom_flag}")
            lines.append(self.dash_line)
            lines.append(f"{space}{n_atom:>6}")

            # Atom types and atom numbers
            lines.append(self.star_line)
            lines.append(f"{space}{self.atom_type_flag}")
            lines.append(self.dash_line)

            for atom, num in data["atom_type_num"].items():
                lines.append(f"{space}{atom:<2} {num:>6}")

            # CTIFOR
            lines.append(self.eq_line)
            lines.append(f"{space}{self.ctifor_flag}")
            lines.append(self.dash_line)
            value = data["ctifor"]
            content_line = self._get_exp_notation(value)
            lines.append(f"{content_line}")

            # Primitive lattice vectors (ang.)
            lines.append(self.eq_line)
            lines.append(f"{space}{self.vec_flag}")
            lines.append(self.dash_line)
            for vector in data["vectors"]:
                content_line = f""
                for value in vector:
                    str_line = self._get_exp_notation(value)
                    content_line += str_line
                lines.append(content_line)

            # Atomic positions (ang.)
            lines.append(self.eq_line)
            lines.append(f"{space}{self.pos_flag}")
            lines.append(self.dash_line)
            for position in data["positions"]:
                content_line = f""
                for value in position:
                    str_line = self._get_exp_notation(value)
                    content_line += str_line
                lines.append(content_line)
    
            # Total energy (eV)
            lines.append(self.eq_line)
            lines.append(f"{space}{self.energy_flag}")
            lines.append(self.dash_line)
            value = data["energy"]
            content_line = self._get_exp_notation(value)
            lines.append(f"{content_line}")
    
            # Forces (eV ang.^-1)
            lines.append(self.eq_line)
            lines.append(f"{space}{self.force_flag}")
            lines.append(self.dash_line)
            for force in data["forces"]:
                content_line = f""
                for value in force:
                    str_line = self._get_exp_notation(value)
                    content_line += str_line
                lines.append(content_line)
    
            # Stress (kbar)
            lines.append(self.eq_line)
            lines.append(f"{space}{self.stress_flag}")
            lines.append(self.dash_line)
            lines.append(f"{space}XX YY ZZ")
            lines.append(self.dash_line)
            content_line = f""
            for value in data["stress"][0:3]:
                str_line = self._get_exp_notation(value)
                content_line += str_line
            lines.append(content_line)
            lines.append(self.dash_line)
            lines.append(f"{space}XY YZ ZX")
            lines.append(self.dash_line)
            content_line = f""
            for value in data["stress"][3:]:
                str_line = self._get_exp_notation(value)
                content_line += str_line
            lines.append(content_line)

        with open(db_path, 'w') as file:
            for line in lines:
                file.write(f"{line}\n")
