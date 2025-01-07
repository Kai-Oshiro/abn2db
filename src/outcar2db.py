#!/usr/bin/env python3
import os
import ase
import argparse

from module.outcar import Outcar
from module.db import Database

def parse_slice(slice_str):
    """Parse a slice string like '1:3:2' or '-3:' into a slice object."""
    parts = slice_str.split(':')
    start = int(parts[0]) if parts[0] else None
    end = int(parts[1]) if len(parts) > 1 and parts[1] else None
    step = int(parts[2]) if len(parts) > 2 and parts[2] else None
    return slice(start, end, step)

def main():
    parser = argparse.ArgumentParser()
    # Positional arguments
    parser.add_argument("outcar_files", type=str, nargs="+",
                        help="Path of OUTCAR file to be loaded")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default=None,
                        help="Name of new ASE database file.")

    parser.add_argument("-is", "--ionic_step", type=str, nargs="+", default=None,
                        help="Ionic step you want to get (e.g., '1:3', '1 3 5' or '-1').\n\
                        To specify a range with negative value,\
                        enclose the range in quotation marks and put leading spaces,\
                        e.g., \' -3:-1\'.")

    # Parse the arguments
    args = parser.parse_args()

    outcar_files = []
    for outcar_file in args.outcar_files:
        outcar_files.append(os.path.abspath(outcar_file))

    indices = None
    if args.ionic_step:
        indices = []
        for ionic_step in args.ionic_step:
            if ":" in ionic_step:
                indices.append(parse_slice(ionic_step))
            else:
                indices.append(int(ionic_step.strip()))

    oc = Outcar()

    all_outcar_data = []
    for outcar_path in outcar_files:
        outcar_data = oc.read_outcar(outcar_path)

        if indices:
            data_to_process = []
            for index in indices:
                if isinstance(index, slice):
                    data_to_process.extend(outcar_data[index])
                else:
                    data_to_process.append(outcar_data[index])
        else:
            data_to_process = outcar_data

        all_outcar_data.extend(data_to_process)

    last_ionic_step = outcar_data[-1]
    for key, value in last_ionic_step.items():
        print(f"{key}: {value}")

    for data in all_outcar_data:
        print(f"ionic_step: {data['ionic_step']}")

    header_data, training_data = oc.parse_data(all_outcar_data)

if __name__ == "__main__":
    main()
