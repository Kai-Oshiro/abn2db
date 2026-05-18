#!/usr/bin/env python3
import argparse

from utils.plot_support import read_ase_db, plot_energies


def main():
    parser = argparse.ArgumentParser(
        description="Create an energy parity plot from two ASE database files."
    )
    parser.add_argument("dft_db_file", type=str, help="Path to DFT ASE database file.")
    parser.add_argument("mlff_db_file", type=str, help="Path to MLFF ASE database file.")
    parser.add_argument(
        "-mm",
        "--max-min",
        type=float,
        nargs=2,
        default=None,
        help="Maximum and minimum values for plot axes.",
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=float,
        default=25,
        help="Tick interval for both axes.",
    )
    parser.add_argument(
        "-c",
        "--color",
        type=str,
        default="C0",
        help="Matplotlib color string for points.",
    )
    parser.add_argument("-fs", "--fontsize", type=int, default=18, help="Font size.")
    parser.add_argument(
        "-ls", "--labelsize", type=int, default=14, help="Tick/annotation size."
    )
    parser.add_argument("-sh", "--show", action="store_true", help="Show the plot.")
    parser.add_argument("-s", "--save", action="store_true", help="Save the plot.")
    parser.add_argument(
        "-fn",
        "--fig-name",
        type=str,
        default="energies_comparison.png",
        help="Output figure file name.",
    )

    args = parser.parse_args()

    energies1, _, natoms1 = read_ase_db(args.dft_db_file)
    energies2, _, natoms2 = read_ase_db(args.mlff_db_file)

    plot_energies(
        energies1=energies1,
        energies2=energies2,
        natoms1=natoms1,
        natoms2=natoms2,
        max_min_list=args.max_min,
        interval=args.interval,
        color=args.color,
        fontsize=args.fontsize,
        labelsize=args.labelsize,
        show=args.show,
        save=args.save,
        fig_name=args.fig_name,
    )


if __name__ == "__main__":
    main()
