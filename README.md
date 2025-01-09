# abn2db
## Overview

The `abn2db` library is a collection of Python scripts designed to handle the conversion, merging, and shuffling of training data in ML_ABN files. These scripts facilitate the manipulation of data files used in machine learning workflows.

> Please note that this code may be verbose and not optimized, which could result in longer processing times for merging large ML_ABN files. 
> 
> For a potentially more efficient solution, you might consider using the pymlff library available at [https://github.com/utf/pymlff](https://github.com/utf/pymlff).

## Scripts

The following script allows checking arguments using the `-h` flag.

### merge_abn.py

This script merges multiple ML_ABN files into a single file. It converts the input files to intermediate database files, merges them, and then converts the merged database back to an ML_ABN file.

**Usage:**
```sh
python merge_abn.py <abn_files> [-fn <file_name>] [-sdb]
```

**Arguments:**
- `<abn_files>`: List of ML_ABN files to merge.
- `-fn, --file_name`: Name of the new ML_ABN file.
- `-sd, --save_db`: Save intermediate database files.

### outcar2abn.py

This script converts OUTCAR files to ML_ABN files. It reads the OUTCAR files, extracts the necessary data, and writes it to a new ML_ABN file.

**Usage:**
```sh
python outcar2abn.py <outcar_files> [-fn <file_name>] [-is <ionic_step>] [-b <basis>]
```

**Arguments:**
- `<outcar_files>`: Path of OUTCAR files to be loaded.
- `-fn, --file_name`: Name of the new ML_ABN file.
- `-is, --ionic_step`: Ionic steps to extract.
- `-b, --basis`: Atom indices for the basis set of training data.

### shuffle_abn.py

This script shuffles the data within an ML_ABN file. It converts the file to an intermediate database, shuffles the data, and converts it back to an ML_ABN file.

**Usage:**
```sh
python shuffle_abn.py <abn_file> [-fn <file_name>] [-s <seed>] [-sd]
```

**Arguments:**
- `<abn_file>`: ML_ABN file to shuffle.
- `-fn, --file_name`: Name of the new shuffled ML_ABN file.
- `-s, --seed`: Seed for the random number generator.
- `-sd, --save_db`: Save intermediate database files.

## Installation

To clone the repository, follow these steps:
1. Open your terminal or command prompt.
2. Navigate to the directory where you want to clone the repository.
3. Run the following command:
    ```sh
    git clone https://github.com/Kai-Oshiro/abn2db.git
    ```
This will create a local copy of the repository in your specified directory.

## License

This project is licensed under the <XXX> License.
