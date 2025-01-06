#!/usr/bin/env python3
import os
import ase
import argparse

from module.outcar import Outcar
from module.db import Database

def main():
    parser = argparse.ArgumentParser()
    # Positional arguments
    parser.add_argument("outcar_files", type=str, nargs='+',
                        help="Path of OUTCAR file to be loaded")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default=None,
                        help="Name of new ASE database file.")

    # Parse the arguments
    args = parser.parse_args()

    outcar_files = []
    for outcar_file in args.outcar_files:
        outcar_files.append(os.path.abspath(outcar_file))

    for outcar_path in outcar_files:
        oc = Outcar()
        entire_data = oc.read_outcar(outcar_path)

    last_ionic_step = entire_data[-1]
    for key, value in last_ionic_step.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
