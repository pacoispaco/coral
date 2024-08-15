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


class SofWbl(object):
    """Representation of IOC World Bird List"""

    def __init__(self):
        self.taxonomy = []
        self.index = {}
        self.version = None
        self.stats = {'order_count': 0,
                      'family_count': 0,
                      'species_count': 0}


def write_taxon_to_file(directory, taxon):
    """Write the JSON representation of 'taxon' to file."""
    for subtaxon in taxon['subtaxa']:
        write_taxon_to_file(directory, subtaxon)
    if taxon['rank'] == "Species":
        fname = taxon['binomial_name'].replace(" ", "_") + ".json"
    else:  # Order or family
        fname = taxon['name'] + ".json"
    subtaxa_files = []
    for subtaxon in taxon['subtaxa']:
        if subtaxon['rank'] == "Species":
            subtaxa_files.append(subtaxon['binomial_name'].replace(" ", "_"))
        else:  # Order or family
            subtaxa_files.append(subtaxon['name'] + ".json")
    taxon['subtaxa'] = subtaxa_files
    f = open(os.path.join(directory, fname), 'w')
    f.write(json.dumps(taxon))
    f.close()


def write_taxonomy_to_files(sofwbl, verbose):
    """Write JSON representations of the taxa in SOF taxonomy to files."""
    p = os.path.join(DEFAULT_DATA_DIR, DEFAULT_SOF_TAXONOMY_DIR)
    if verbose:
        print("Writing to files ...")
    if os.path.exists(p):
        print("Error: Directory '%s' already exists." % (p))
        sys.exit(ERROR_DATA_DIR_EXISTS_ALREADY)
    else:
        os.makedirs(p)
    f = open(os.path.join(p, VERSION_FILE_NAME), 'w')
    v = {"version": sofwbl.version}
    f.write(json.dumps(v))
    f.close()
    for taxon in sofwbl.taxonomy:
        write_taxon_to_file(p, taxon)


def load_sof_subtaxa(sofwbl, taxon, sof_dir):
    """Load the subtaxa for the given taxon."""
    i = 0
    for name in taxon['subtaxa']:
        f = open(os.path.join(sof_dir, name))
        t = json.load(f)
        f.close()
        taxon['subtaxa'][i] = t
        if t['rank'] == "Order":
            sofwbl.stats['order_count'] += 1
        elif t['rank'] == "Family":
            sofwbl.stats['family_count'] += 1
        elif t['rank'] == "Species":
            sofwbl.stats['species_count'] += 1
        load_sof_subtaxa(sofwbl, t, sof_dir)
        i += 1


def load_sof_taxonomy(sofwbl, sof_dir, verbose):
    """Load SOF taxonomy from files."""
    # Read version
    p = os.path.join(DEFAULT_DATA_DIR, DEFAULT_SOF_TAXONOMY_DIR)
    f = open(os.path.join(p, VERSION_FILE_NAME))
    sofwbl.version = json.load(f)["version"]
    f.close()
    # Read orders:
    p = os.popen("grep -l '\"rank\": \"Order\"' %s/*.json" % (sof_dir))
    filenames = p.read().split()
    p.close()
    for fname in filenames:
        f = open(fname)
        taxon = json.load(f)
        f.close()
        sofwbl.taxonomy.append(taxon)
        load_sof_subtaxa(sofwbl, taxon, sof_dir)
        sofwbl.stats['order_count'] += 1


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
    sofwbl = SofWbl()
    sof_file = soffiles.sof_file(filepath)

    if verbose:
        print(f"Reading SOF Master File '{sof_file.path}' ...")
        print(f"SOF Version: {sof_file.version}")
        sof_file.read()
        sofwbl.taxonomy = sof_file.taxonomy
        sofwbl.index = sof_file.index
        sofwbl.stats = sof_file.taxonomy_stats
        sofwbl.version = sof_file.version

    if not dry_run:
        if write:
            write_taxonomy_to_files(sofwbl, verbose)
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
