import os
import re

from ase import Atoms
from ase.calculators.singlepoint import SinglePointDFTCalculator
from ase.db import connect

class Outcar2:
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

        file_name = os.path.basename(outcar_path)

        with open(outcar_path, "r") as f:
            lines = f.readlines()

        # Get common parameters
        element_list = []
        mass = []
        for idx, line in enumerate(lines):
            if self.atom_type_tag in line:
                match = re.search(r"=(.*?):", line)
                element_list.append(match.group(1).strip())

            if self.mass_tag in line:
                mass_line = lines[idx].split(";")[0]
                mass_line = mass_line.replace("POMASS =", "").strip()
                mass.append(float(mass_line))

            if self.n_atom_tag in line:
                n_atom = int(line.split()[-1])

            if self.n_atom_per_type_tag in line:
                n_atom_per_type = list(map(int, line.split("=")[1].split()))

                if len(element_list) != len(n_atom_per_type):
                    raise ValueError("Number of atom types and number of atoms per type do not match.")

                n_atom_type = len(element_list)
                atom_type_num = dict(zip(element_list, n_atom_per_type))

            if self.system_tag in line:
                sys_name = line.replace(self.system_tag, "").strip()

                break

        # Add common parameters to the dictionary
        common_data = {"file_name": file_name}
        common_data["mass"] = mass
        common_data["n_atom"] = n_atom
        common_data["n_atom_type"] = n_atom_type
        common_data["atom_type_num"] = atom_type_num
        common_data["sys_name"] = sys_name

        # Get DFT and MLFF results
        outcar_data = []
        is_dft = False
        is_step = False
        for idx, line in enumerate(lines):
            if self.ionic_step_tag in line:
                ionic_step = int(line.split()[-2])

                is_step = True

            # Skip the header section of OUTCAR
            if not is_step:
                continue

            if self.dft_section_flag in line:
                is_dft = True

            if self.mlff_section_flag in line:
                is_dft = False

            # Get DFT and MLFF results
            if self.stress_tag in line:
                stress = [float(x) for x in lines[idx].split()[2:8]]

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

    def write2db(self, outcar_data, db_path, data_type):
        db = connect(db_path)

        for data in outcar_data:
            data_type = data_type.lower()
            if data_type.startswith("d") and not data["is_dft"]:
                continue
            elif data_type.startswith("m") and data["is_dft"]:
                continue

            chemical_symbols = []
            for element, num in data["atom_type_num"].items():
                chemical_symbols.extend([element] * num)

            vectors = data["vectors"]
            positions = data["positions"]

            atoms = Atoms(
                chemical_symbols, 
                positions=positions, 
                cell=vectors, 
                pbc=True
                )

            free_energy = data["free_energy"]
            energy = data["energy"]
            forces = data["forces"]
            stress = data["stress"]

            calculator = SinglePointDFTCalculator(
                atoms,
                free_energy=free_energy,
                energy=energy,
                forces=forces,
                stress=stress
                )

            atoms.set_calculator(calculator)
            atoms.calc.name = "vasp"

            sys_name = data["sys_name"]
            ionic_step = data["ionic_step"]
            file_name = data["file_name"]
            is_dft = data["is_dft"]

            db.write(
                atoms,
                sys_name=sys_name,
                ionic_step=ionic_step,
                file_name=file_name,
                is_dft=is_dft
                )

