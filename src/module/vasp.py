import os
import subprocess

import numpy as np

from ase import Atoms
from ase.io.vasp import write_vasp
from ase.calculators.calculator import Calculator, all_changes

from . import outcar

class VaspCalculator(Calculator):
    def __init__(self, 
        command="mpirun -np", 
        n_core=4, 
        vasp_path="vasp_std", 
        work_dir="./", 
        make_poscar=False
        **kwargs
        ):

        self.results = {}

        super().__init__(**kwargs)

        self.normal_termination_flag = "General timing and accounting informations for this job:"
        self.opt_convergence_flag = "reached required accuracy - stopping structural energy minimisation"
        self.elapsed_time_flag = "Elapsed time (sec):"

        self.command = f"{command} {n_core} {vasp_path}"
        self.work_dir = os.path.abspath(work_dir)
        self.make_poscar = make_poscar

        self.poscar_path = os.path.join(self.work_dir, "POSCAR")
        self.outcar_path = os.path.join(self.work_dir, "OUTCAR")
        self.out_path = os.path.join(self.directory, "vasp.out")

    def clear_results(self):
        self.results.clear()

    def check_convergence(self):
        with open(self.outcar_path, "r") as f:
            lines = f.readlines()

        normal_termination = False
        opt_convergence = False
        elapsed_time = None
        for line in lines:
            if self.normal_termination_flag in line:
                normal_termination = True

            if self.opt_convergence_flag in line:
                opt_convergence = True

            if self.elapsed_time_flag in line:
                elapsed_time = float(line.split()[-1]) / 3600

        convergence_info = {
            "normal_termination": normal_termination,
            "opt_convergence": opt_convergence,
            "elapsed_time": elapsed_time
        }

        return convergence_info

    def calculate(self, 
        atoms=None, 
        properties=("energy", "forces"),
        system_changes=tuple(all_changes)
        ):

        super().calculate(atoms, properties, system_changes)

        if atoms is not None:
            self.atoms = atoms.copy()

        self.clear_results()

        # Write POSCAR file
        if self.make_poscar:
            write_vasp(self.poscar_path, self.atoms)

        # Execute VASP
        subproc = subprocess.run(command, shell=True, capture_output=True, text=True)

        # Write the stdout to the file
        with open(self.out_path, "w") as f:
            f.write(subproc.stdout)

        # Parse the OUTCAR file
        convergence_info = self.check_convergence()

        oc = outcar.Outcar(self.outcar_path)
        outcar_data = os.load()

        self.results_dict = outcar_data[-1]
        self.results_dict["normal_termination"] = convergence_info["normal_termination"]
        self.results_dict["opt_convergence"] = convergence_info["opt_convergence"]
        self.results_dict["elapsed_time"] = convergence_info["elapsed_time"]

        # Return the results to the ASE
        self.results["energy"] = self.last_data.get("energy", None)
        self.results["free_energy"] = self.last_data.get("free_energy", None)
        self.results["forces"] = np.array(self.last_data.get("forces", []))
        self.results["stress"] = np.array(self.last_data.get("stress", []))

    def get_results(self):
        return self.results_dict
