#!/usr/bin/env python3
import os
import random
import argparse
from ase.db import connect

def shuffle_db(input_file, output_file, index_file, seed=None):
    db = connect(input_file)
    rows = list(db.select())
    original_indices = list(range(len(rows)))

    if seed is not None:
        random.seed(seed)

    shuffled_indices = original_indices[:]
    random.shuffle(shuffled_indices)

    new_db = connect(output_file, use_lock_file=False)
    for i in shuffled_indices:
        row = rows[i]
        new_db.write(row.toatoms(), key_value_pairs=row.key_value_pairs, data=row.data)

    with open(index_file, 'w') as f:
        for original, shuffled in sorted(zip(original_indices, shuffled_indices), key=lambda x: x[1]):
            f.write(f"{shuffled + 1} => {original + 1}\n")

def main():
    parser = argparse.ArgumentParser(description="Shuffle rows in an ASE database file.")
    # Positional arguments
    parser.add_argument("db_file", type=str,
                        help="Path of ASE database file.")

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