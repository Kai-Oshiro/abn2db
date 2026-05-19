# abn2db

## Overview

`abn2db` is a collection of Python scripts for handling VASP-related training data through conversions between `ML_ABN` and ASE database (`.db`) files.

The toolkit covers:
- Conversion between `ML_ABN` and ASE database files
- Data extraction from VASP `OUTCAR`
- Merging and shuffling datasets
- Running VASP calculations from structures in an ASE database
- Energy/force parity plotting from two ASE databases

> Note: This code is relatively verbose and has not been fully optimized. Therefore, merging large ML_ABN files may require considerable processing time.
> 
> For a potentially more efficient alternative, please consider using the pymlff library:  
> https://github.com/utf/pymlff

## Design Concept

The core design is to use ASE database files (`ase.db`) as an intermediate format between workflows and `ML_ABN` files.

This design is intended to make it easier to bridge data from software other than VASP into `ML_ABN` by going through an ASE database. However, MLFF training with results from non-VASP software has not yet been tested in this project.

If you want to use results from software other than VASP, you need to prepare ASE database files by yourself with the required properties used by these scripts.

## Verified Environment

The following versions have been verified:
- Python: `3.8.18`
- numpy: `1.24.4`
- matplotlib: `3.5.3`
- ase: `3.22.1`
- VASP: `6.4.2`

## Typical Workflow

A typical usage flow is:

1. Prepare data in ASE database format.
   - From `ML_ABN`: `abn2db.py`
   - From `OUTCAR`: `outcar2db.py` or `get_fp_data.py`
2. Merge or shuffle data if needed.
   - Merge: `merge_db.py` (or `merge_abn.py`)
   - Shuffle: `shuffle_db.py` (or `shuffle_abn.py`)
3. Convert ASE database to `ML_ABN` when needed.
   - `db2abn.py`
4. Optionally evaluate with parity plots.
   - `energy_parity_plot.py`, `force_parity_plot.py`

For script-specific options, run each script with `-h`.

## Script Reference

### Core functionality

#### `abn2db.py`

Converts an `ML_ABN` file to an ASE database file.

Main information written into each ASE DB row includes:
- Row-level properties such as `sys_name`, `conf_num`, and `ctifor`
- Atomic structure (`numbers`, `positions`, `cell`, `pbc`)
- Calculation data (`free_energy`, `forces`, `stress`)
- Extra metadata in `data`:
  - `basis`
  - `ref_energy`
  - `mass`

Usage:
```bash
python src/abn2db.py <abn_file> [-fn <file_name>]
```

#### `db2abn.py`

Converts an ASE database file to an `ML_ABN` file.

Expected/required data per row includes structure plus energy/force/stress-related properties used for `ML_ABN` reconstruction. The script also handles missing fields with defaults used in `utils/db.py`, for example:
- Missing `ctifor` -> `0.002` (default `ML_CTIFOR` value)
- Missing `basis` in `row.data` -> empty basis per element
- Missing `ref_energy` -> zero-filled list
- Missing `mass` -> atomic masses derived from element types

Usage:
```bash
python src/db2abn.py <db_file> [-fn <file_name>]
```

### Main scripts for VASP files

#### `merge_abn.py`

Merges multiple `ML_ABN` files into one. Internally converts each input to ASE DB, merges DB rows, and converts the merged DB back to `ML_ABN`.

Usage:
```bash
python src/merge_abn.py <abn_files> [-fn <file_name>] [-sd]
```

#### `merge_db.py`

Merges multiple ASE database files into one ASE database by copying all rows.

Usage:
```bash
python src/merge_db.py <db_files> [-fn <file_name>]
```

#### `outcar2abn.py`

Extracts data from one or more `OUTCAR` files and writes an `ML_ABN` file. You can filter ionic steps, choose basis atom indices, and select `dft`/`mlff`/`both` data.

Usage:
```bash
python src/outcar2abn.py <outcar_files> [-fn <file_name>] [-is <ionic_step>] [-b <basis>] [-m <method>]
```

#### `outcar2db.py`

Extracts data from one or more `OUTCAR` files and writes an ASE database file. Supports ionic-step filtering, basis selection, and `dft`/`mlff`/`both` filtering.

Usage:
```bash
python src/outcar2db.py <outcar_files> [-fn <file_name>] [-is <ionic_step>] [-b <basis>] [-m <method>]
```

#### `get_fp_data.py`

Extracts first-principles data from on-the-fly training `OUTCAR` files and writes it to an ASE database file. Default extraction target is `dft`.

Usage:
```bash
python src/get_fp_data.py <outcar_files> [-fn <file_name>] [-is <ionic_step>] [-m <method>]
```

### Support scripts

#### `execute_vasp.py`

Runs VASP for structures stored in an ASE database and writes calculation results to a new ASE database. Supports custom VASP command, working directory, and optional I/O file retention.

Usage:
```bash
python src/execute_vasp.py <db_file> [-fn <file_name>] [-c <command>] [-wd <work_dir>] [-si <save_io>]
```

#### `shuffle_abn.py`

Shuffles configurations in an `ML_ABN` file using ASE DB as an intermediate format, and writes shuffled output plus index mapping.

Usage:
```bash
python src/shuffle_abn.py <abn_file> [-fn <file_name>] [-s <seed>] [-sd]
```

#### `shuffle_db.py`

Shuffles rows in an ASE database file and writes a shuffled DB and index mapping file.

Usage:
```bash
python src/shuffle_db.py <db_file> [-fn <file_name>] [-if <index_file>] [-s <seed>]
```

#### `energy_parity_plot.py`

Creates an energy parity plot from two ASE database files.

Usage:
```bash
python src/energy_parity_plot.py <dft_db_file> <mlff_db_file> [-mm <max min>] [-i <interval>] [-c <color>] [-fs <fontsize>] [-ls <labelsize>] [-sh] [-s] [-fn <fig_name>]
```

#### `force_parity_plot.py`

Creates a force parity plot from two ASE database files.

Usage:
```bash
python src/force_parity_plot.py <dft_db_file> <mlff_db_file> [-mm <max min>] [-i <interval>] [-c <color_x color_y color_z>] [-fs <fontsize>] [-ls <labelsize>] [-sh] [-s] [-fn <fig_name>]
```

## Examples

Currently under preparation.

## License

This project is licensed under the MIT License.

## Related Literatures

- ChemRxiv: https://doi.org/10.26434/chemrxiv.15003015/v1
- Zenodo: https://doi.org/10.5281/zenodo.20033455
