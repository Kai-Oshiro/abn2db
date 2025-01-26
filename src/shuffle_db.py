#!/usr/bin/env python3
import os
import argparse

from module.support import shuffle_db

def main():
    parser = argparse.ArgumentParser(description="Shuffle rows in an ASE database file.")
    # Positional arguments
    parser.add_argument("db_file", type=str,
                        help="Path to ASE database file.")

    # Optional arguments
    parser.add_argument("-fn", "--file_name", type=str, default=None,
                        help="Name of new shuffled ML_ABN file")

    parser.add_argument("-if", "--index_file", type=str, default=None,
                        help="Specify a file to save original and shuffled indexes.")

    parser.add_argument("-s", "--seed", type=int, default=1,
                        help="Seed for the random number generator.")

    args = parser.parse_args()

    db_path = args.db_file
    db_path = os.path.abspath(db_path)

    shuffled_db = args.file_name
    if shuffled_db is None:
        shuffled_db = os.path.basename(db_path).split(".")[0] + "_shuffled.db"

    if not shuffled_db.endswith(".db"):
        shuffled_db += ".db"

    idx_file = args.index_file
    if idx_file is None:
        idx_file = os.path.basename(db_path).split(".")[0] + "_shuffled.txt"

    if not idx_file.endswith(".txt"):
        idx_file += ".txt"

    shuffle_db(db_path, shuffled_db, idx_file, args.seed)

if __name__ == '__main__':
    main()