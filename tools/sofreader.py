#!/usr/bin/env python3

"""This program reads SOF (Birdlife Sweden) name list files containing Swedish names and prints
   JSON representations of that data to stdout, or to files."""

import argparse
import os
import os.path
import sys
import json
import soffiles

# Error constants
ERROR_FILE_NOT_FOUND = 1
ERROR_FILE_NOT_EXCEL = 2
ERROR_DATA_DIR_EXISTS_ALREADY = 3
ERROR_NO_MASTER_DATA = 4

# Directory and file name constants
DEFAULT_DATA_DIR = "./gendata"
DEFAULT_SOF_TAXONOMY_DIR = "sof"
VERSION_FILE_NAME = "version.json"


def print_to_stdout(sofwbl, verbose):
    """Print JSON representations to stdout."""
    if verbose:
        print("Printing to stdout ...")
    print(json.dumps(sofwbl.taxonomy, indent=2))


def print_taxonomy_info(sofwbl, verbose):
    """Print info on SOF taxonomy to stdout."""
    print("Taxonomy statistics:")
    print("  Taxonomy: SOF %s" % (sofwbl.version))
    print("  Orders: %d" % (sofwbl.stats['order_count']))
    print("  Families: %d" % (sofwbl.stats['family_count']))
    print("  Species: %d" % (sofwbl.stats['species_count']))
    print("  Total number of taxa: %d" % (sofwbl.stats['family_count'] +
                                          sofwbl.stats['order_count'] +
                                          sofwbl.stats['species_count']))


def handle_files(filepath, write, info, verbose, dry_run):
    """Handle the SOF file. if 'write' then write data to files. If 'info'
       then print information on the contents of the files. If 'verbose'
       then print information on progress and what's happening. If 'dry_run'
       don't write taxonomy info to files or to stdout."""
    if dry_run:
        print("Dry-run: No taxonomy information will be written to files or to stdout")
    if verbose:
        print(f"SOF file: {filepath}")
    sof_file = soffiles.SofNamesFile(filepath)

    if verbose:
        print(f"Reading SOF Master File '{sof_file.path}' ...")
        print(f"SOF Version: {sof_file.version}")
    sof_file.read()

    sofwbl = sof_file.sofwbl
    if not dry_run:
        if write:
            p = os.path.join(DEFAULT_DATA_DIR, DEFAULT_SOF_TAXONOMY_DIR)
            if os.path.exists(p):
                print("Error: Directory '%s' already exists." % (p))
                sys.exit(ERROR_DATA_DIR_EXISTS_ALREADY)
            else:
                if verbose:
                    print("Writing files ...")
                os.makedirs(p)
                sofwbl.write_to_files(p, VERSION_FILE_NAME)
        else:
            print_to_stdout(sofwbl, verbose)
    if info:
        print_taxonomy_info(sofwbl, verbose)


def main():
    parser = argparse.ArgumentParser(description='Read SOF Bird Names List\
                                      file and print JSON representations of\
                                      the contents to stdout or to files. If\
                                      the -w option is not chosen it will print\
                                      to stdout.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="print info about what's going on [False]")
    parser.add_argument('-d', '--dry-run', action='store_true', default=False,
                        help="do not write any taxonomy files or print them to stdout [False]")
    parser.add_argument('-i', '--info', action='store_true', default=False,
                        help="print info about the SOF file [False]")
    parser.add_argument('-w', '--write', action='store_true', default=False,
                        help="write to JSON files [False]")
    parser.add_argument('sof_file', help="SOF file to read")
    args = parser.parse_args()
    # First check if the file exist
    if not os.path.isfile(args.sof_file):
        print(f"Error: File '{args.sof_file}' not found.")
        sys.exit(ERROR_FILE_NOT_FOUND)
    # Then read the files in correct order
    handle_files(args.sof_file, args.write, args.info, args.verbose, args.dry_run)


if __name__ == "__main__":
    main()
