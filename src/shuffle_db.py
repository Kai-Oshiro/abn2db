#!/usr/bin/env python3
import argparse
import random
from ase.db import connect

def shuffle_db(input_file, output_file, seed=None):
    db = connect(input_file)
    rows = list(db.select())
    
    if seed is not None:
        random.seed(seed)
    
    random.shuffle(rows)
    
    new_db = connect(output_file, use_lock_file=False)
    for row in rows:
        new_db.write(row.toatoms(), key_value_pairs=row.key_value_pairs, data=row.data)

def main():
    parser = argparse.ArgumentParser(description='Shuffle rows in an ASE database file.')
    parser.add_argument('input_file', type=str, help='The input ASE database file.')
    parser.add_argument('-of', '--output_file', type=str, help='The output ASE database file with shuffled rows.', default=None)
    parser.add_argument('-s', '--seed', type=int, help='The seed for the random number generator.', default=1)
    
    args = parser.parse_args()

    if args.output_file is None:
        args.output_file = args.input_file.split(".")[0] + "_shuffled.db"

    shuffle_db(args.input_file, args.output_file, args.seed)

if __name__ == '__main__':
    main()