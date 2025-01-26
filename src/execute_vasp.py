#!/usr/bin/env python3
import os
import argparse

from ase import Atoms

from module.vasp import VaspCalculator

def main():
    parser = argparse.ArgumentParser(description="Perform ab initio calculation on structures in ase db file.")
    # Positional arguments
    parser.add_argument("db_file", type=str,
                        help="Path to ASE database file to be loaded.")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default="results.db",
                        help="Name of the database file that will contain calculation results")
    parser.add_argument("-c", "--command", type=str, default="mpirun -np",
                        help="Command to run VASP.")
    parser.add_argument("-n", "--n_core", type=int, default=4,
                        help="Number of cores to use.")
    parser.add_argument("-vp", "--vasp_path", type=str, default="vasp_std",
                        help="Path to VASP executable.")
    parser.add_argument("-wd", "--work_dir", type=str, default="./",
                        help="Path to working directory.")

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
    new_db = connect(new_db_path)

    command = args.command
    n_core = args.n_core
    vasp_path = args.vasp_path

    for row in db.select():
        ref_atoms = row.toatoms()
        chemical_symbols = ref_atoms.get_chemical_symbols()
        cell = row.toatoms().get_cell()
        positions = row.toatoms().get_positions()
        sys_name = row.sys_name
        ionic_step = row.ionic_step

        atoms = Atoms(
            symbols=chemical_symbols, 
            cell=cell, 
            positions=positions,
            pbc=True
            )

        calc = VaspCalculator(
            command=command, 
            cores=n_core, 
            vasp_path=vasp_path, 
            work_dir=work_dir
            make_poscar=True
            )

        atoms.set_calculator(calc)
        atoms.calc.name = "vasp"
        atoms.get_potential_energy()

        results_dict = calc.get_results()

        new_db.write(atoms,
            sys_name=sys_name,
            ionic_step=ionic_step,
            is_dft=result_dict["is_dft"],
            )

if __name__ == "__main__":
    main()