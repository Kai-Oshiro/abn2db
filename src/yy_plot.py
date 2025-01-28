#!/usr/bin/env python3
import argparse

from module.plot_support import read_ase_db, plot_energies, plot_forces

def main():
    parser = argparse.ArgumentParser(description="Plot energies and forces from two ASE database files.")
    # Positional arguments
    parser.add_argument("dft_db_file", type=str,
                        help="Path to ASE database file.")
    parser.add_argument("mlff_db_file", type=str,
                        help="Path to ASE database file.")

    args = parser.parse_args()
    db_file1 = args.dft_db_file
    db_file2 = args.mlff_db_file

    energies1, forces1, natoms1 = read_ase_db(db_file1)
    energies2, forces2, natoms2 = read_ase_db(db_file2)

    plot_energies(energies1, energies2, natoms1, natoms2, save=True)
    print("Plotted energies comparison.")
    plot_forces(forces1, forces2, natoms1, natoms2, save=True)
    print("Plotted forces comparison.")

if __name__ == "__main__":
    main()
