#!/usr/bin/env python3

"""This program reads IOC World Bird List files and prints JSON representations
   of that data to stdout, or to files."""

import argparse
import os
import os.path
import sys
import json
import iocfiles

# Error constants
ERROR_NO_MASTER_FILE_GIVEN = 1
ERROR_FILE_NOT_FOUND = 2
ERROR_FILE_NOT_EXCEL = 3
ERROR_DATA_DIR_EXISTS_ALREADY = 4
ERROR_NO_MASTER_DATA = 5
ERROR_FILE_VERSION_MISMATCH = 6

# Directory and file name constants
DEFAULT_DATA_DIR = "./gendata"
DEFAULT_IOC_TAXONOMY_DIR = "ioc"
VERSION_FILE_NAME = "version.json"


def print_to_stdout(iocwbl, verbose):
    """Print JSON representations to stdout."""
    if verbose:
        print("Printing to stdout ...")
    print(json.dumps(iocwbl.taxonomy, indent=2))


def print_taxonomy_info(iocwbl, verbose):
    """Print info on IOC taxonomy to stdout."""
    print("Taxonomy statistics:")
    print(f"  Taxonomy: IOC {iocwbl.version}")
    print(f"  Infraclasses: {iocwbl.stats['infraclass_count']}")
    print(f"  Orders: {iocwbl.stats['order_count']}")
    print(f"  Families: {iocwbl.stats['family_count']}")
    print(f"  Genus: {iocwbl.stats['genus_count']}")
    print(f"  Species: {iocwbl.stats['species_count']}")
    print(f"  Subspecies: {iocwbl.stats['subspecies_count']}")
    count = iocwbl.stats['infraclass_count'] + \
        iocwbl.stats['family_count'] + \
        iocwbl.stats['order_count'] + \
        iocwbl.stats['genus_count'] + \
        iocwbl.stats['species_count'] + \
        iocwbl.stats['subspecies_count']
    print(f"  Total number of taxa: {count}")


def file_versions_are_consistent(ioc_files):
    """Returns true if all `version` values in the list of Ioc*File objects in `ioc_files` have
       the same value."""
    version_values = [file.version for file in ioc_files]
    return len(set(version_values)) <= 1


def handle_files(filepaths, write, output_dir, info, verbose, dry_run):
    """Handle the IOC files. if 'write' then write data to files. If 'info'
       then print information on the contents of the files. If 'verbose'
       then print information on progress and what's happening. If 'dry_run'
       don't write taxonomy info to files or to stdout."""
    if verbose:
        if dry_run:
            print("Dry-run: No taxonomy information will be written to files or to stdout")
        print(f"IOC files:\n{filepaths}")

    # First read the IOC Master File.
    ioc_master_file = iocfiles.IocMasterFile(filepaths["master-file"])
    ioc_files = [ioc_master_file]
    if verbose:
        print(f"Reading IOC Master File '{ioc_master_file.path}'")
        print(f"IOC Master File Version: {ioc_master_file.version}")
    ioc_master_file.read()
    iocwbl = ioc_master_file.iocwbl
    # Then check if any other of the IOC files are to be read, and do so if specified.
    if filepaths["other-lists-file"]:
        other_lists_file = iocfiles.IocOtherListsFile(filepaths["other-lists-file"], iocwbl)
        if verbose:
            print(f"Reading IOC Other Lists File '{other_lists_file.path}'")
            print(f"IOC Other Lists File Version: {other_lists_file.version}")
        other_lists_file.read()
        ioc_files.append(other_lists_file)
    if filepaths["multilingual-file"]:
        multilingual_file = iocfiles.IocMultilingualFile(filepaths["multilingual-file"], iocwbl)
        if verbose:
            print(f"Reading IOC Multilingual File '{multilingual_file.path}'")
            print(f"IOC Multilingual File Version: {multilingual_file.version}")
        multilingual_file.read()
        ioc_files.append(multilingual_file)
    if filepaths["complimentary-file"]:
        complimentary_file = iocfiles.IocComplementaryFile(filepaths["complimentary-file"], iocwbl)
        if verbose:
            print(f"Reading IOC Complementary File '{complimentary_file.path}'")
            print(f"IOC Complementary File Version: {complimentary_file.version}")
        complimentary_file.read()
        ioc_files.append(complimentary_file)
    # Check that the IOC files have consistent versions
    if not file_versions_are_consistent(ioc_files):
        print("Error: Version mismatch between IOC files.")
        sys.exit(ERROR_FILE_VERSION_MISMATCH)
    # Check to see if we are to write to file or stdout, and do so if requested.
    if not dry_run:
        if write:
            p = os.path.join(output_dir, DEFAULT_IOC_TAXONOMY_DIR)
            if os.path.exists(p):
                print("Error: Directory '%s' already exists." % (p))
                sys.exit(ERROR_DATA_DIR_EXISTS_ALREADY)
            else:
                if verbose:
                    print("Writing files ...")
                os.makedirs(p)
                iocwbl.write_to_files(p, VERSION_FILE_NAME)
        else:
            print_to_stdout(iocwbl, verbose)
    if info:
        print_taxonomy_info(iocwbl, verbose)


def main():
    parser = argparse.ArgumentParser(description='Read IOC World Bird List files and print JSON\
                                      representations of the contents to stdout or to files. If\
                                      the -w option is not chosen it will print to stdout. An IOC\
                                      Master file must always by given as an argument. The other\
                                      three IOC files are optional and are given as separate\
                                      arguments. Use --help for more info.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help="print info about what's going on [False]")
    parser.add_argument('-d', '--dry-run', action='store_true', default=False,
                        help="do not write any taxonomy files or print them to stdout [False]")
    parser.add_argument('-i', '--info', action='store_true', default=False,
                        help="print info about the IOC files [False]")
    parser.add_argument('-w', '--write', action='store_true', default=False,
                        help="write to JSON files [False]")
    parser.add_argument('-o', '--output-dir', default=DEFAULT_DATA_DIR,
                        help=("directory where the output directory with JSON files "
                              f"is written [{DEFAULT_DATA_DIR}]"))
    parser.add_argument('-O', '--other-lists-file', default=None,
                        help="IOC Other Lists file")
    parser.add_argument('-M', '--multilingual-file', default=None,
                        help="IOC Multilingual file")
    parser.add_argument('-C', '--complimentary-file', default=None,
                        help="IOC Complementary file")
    parser.add_argument('ioc_master_file', help="IOC Master file to read")
    args = parser.parse_args()
    # Check that a IOC master file is specified, and add it as the first file to the list of files.
    if not args.ioc_master_file:
        print(f"Error: IOC Master '{args.ioc_master_file}' not given as argument.")
        sys.exit(ERROR_NO_MASTER_FILE_GIVEN)
    # Check if the files exist, and if so, add them to the list of files.
    if not os.path.isfile(args.ioc_master_file):
        print(f"Error: IOC Master file '{args.ioc_master_file}' not found.")
        sys.exit(ERROR_FILE_NOT_FOUND)
    else:
        files = {"master-file": args.ioc_master_file}
    if args.other_lists_file and not os.path.isfile(args.other_lists_file):
        print(f"Error: IOC Other Lists file '{args.other_lists_file}' not found.")
        sys.exit(ERROR_FILE_NOT_FOUND)
    else:
        files["other-lists-file"] = args.other_lists_file
    if args.multilingual_file and not os.path.isfile(args.multilingual_file):
        print(f"Error: IOC Multilingual file '{args.multilingual_file}' not found.")
        sys.exit(ERROR_FILE_NOT_FOUND)
    else:
        files["multilingual-file"] = args.multilingual_file
    if args.complimentary_file and not os.path.isfile(args.complimentary_file):
        print(f"Error: IOC Complimentary file '{args.multilingual_file}' not found.")
        sys.exit(ERROR_FILE_NOT_FOUND)
    else:
        files["complimentary-file"] = args.complimentary_file
    # Then read the files in correct order
    handle_files(files, args.write, args.output_dir, args.info, args.verbose, args.dry_run)


if __name__ == "__main__":
    main()
