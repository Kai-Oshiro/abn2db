#!/usr/bin/env python3
import os
import argparse

from ase import Atoms
from ase.db import connect

from module.vasp import VaspCalculator
from module.support import save_io, delete_io

def main():
    parser = argparse.ArgumentParser(description="Perform VASP on structures in ase db file.")
    # Positional arguments
    parser.add_argument("db_file", type=str,
                        help="Path to ASE database file to be loaded.")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default="results.db",
                        help="Name of the database file that will contain calculation results")

    parser.add_argument("-c", "--command", type=str, default="mpirun -np 4 vasp_std",
                        help="Command to run VASP.")

    parser.add_argument("-wd", "--work_dir", type=str, default="./",
                        help="Path to working directory.")

    parser.add_argument("-si", "--save_io", type=str, nargs="+", default=None,
                        help="IO files to be saved (e.g., 'OUTCAR', 'OSZICAR', 'vasprun.xml', 'CONTCAR', 'POSCAR').")

    # Parse the arguments
    args = parser.parse_args()

    ref_db_path = args.db_file
    ref_db_path = os.path.abspath(ref_db_path)
    ref_db = connect(ref_db_path)

    new_db_name = args.file_name
    if not new_db_name.endswith(".db"):
        new_db_name = new_db_name + ".db"

    work_dir = args.work_dir
    new_db_path = os.path.join(work_dir, new_db_name)
    new_db_path = os.path.abspath(new_db_path)
    if os.path.exists(new_db_path):
        raise FileExistsError(f"{new_db_path} already exists.")

    new_db = connect(new_db_path)

    count = 1
    for row in ref_db.select():
        ref_atoms = row.toatoms()
        chemical_symbols = ref_atoms.get_chemical_symbols()
        cell = row.toatoms().get_cell()
        positions = row.toatoms().get_positions()

        atoms = Atoms(
            symbols=chemical_symbols,
            cell=cell,
            positions=positions,
            pbc=True
        )

        calc = VaspCalculator(
            command=args.command,
            work_dir=work_dir,
            make_poscar=True
        )

        atoms.set_calculator(calc)
        atoms.calc.name = "vasp"
        atoms.get_potential_energy()

        results_dict = calc.get_results()

        ref_db.update(
            row.id,
            common_id=count,
        )

        new_db.write(atoms,
            common_id=count,
            is_dft=results_dict["is_dft"],
            normal_termination=results_dict["normal_termination"],
            opt_convergence=results_dict["opt_convergence"],
            elapsed_time=results_dict["elapsed_time"]
        )

        if args.save_io:
            save_io(work_dir, args.save_io, count)

        delete_io(work_dir)

        count += 1

if __name__ == "__main__":
    main()