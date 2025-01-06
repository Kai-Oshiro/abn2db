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

    parser.add_argument("-is", "--ionic_step", type=str, nargs='+', default=None,
                        help="Ionic step you want to get (e.g., '1:3', '1 3 5' or '-1').\n\
                        To specify a range with negative value,\
                        enclose the range in quotation marks and put leading spaces,\
                        e.g., \" -3:-1\".")

    # Parse the arguments
    args = parser.parse_args()

    outcar_files = []
    print(args.outcar_files)
    for outcar_file in args.outcar_files:
        outcar_files.append(os.path.abspath(outcar_file))

    indices = None
    print(args.ionic_step)
    if args.ionic_step:
        indices = []
        for ionic_step in args.ionic_step:
            if ":" in ionic_step:
                start, end = map(int, ionic_step.split(":"))
                print(f"start: {start}, end: {end}")
                if start < 0: pass
                else: start -= 1
                if end < 0: end += 1
                else: pass
                indices.extend(range(start, end))
            else:
                index = int(ionic_step)
                if index < 0: pass
                else: index -= 1
                indices.append(index)

    all_outcar_data = []
    for outcar_path in outcar_files:
        oc = Outcar()
        outcar_data = oc.read_outcar(outcar_path)

        if indices:
            data_to_process = [outcar_data[i] for i in indices if i < len(outcar_data)]
        else:
            data_to_process = outcar_data

        all_outcar_data.extend(data_to_process)

    #last_ionic_step = outcar_data[-1]
    #for key, value in last_ionic_step.items():
        #print(f"{key}: {value}")

    for data in all_outcar_data:
        print(f"ionic_step: {data['ionic_step']}")

if __name__ == "__main__":
    main()
