#!/usr/bin/env python3

"""This program reads IOC World Bird List files and prints JSON representations
   of that data to stdout, or to files."""

import argparse
import os, os.path, sys
import openpyxl.reader.excel as xlxs
import re
import json
import copy
from iocfiles import *

import pprint

# Error constants
ERROR_FILE_NOT_FOUND = 1
ERROR_FILE_NOT_EXCEL = 2
ERROR_DATA_DIR_EXISTS_ALREADY = 3
ERROR_NO_MASTER_DATA = 4

# Directory and file name constants
DEFAULT_IOC_DIR = "./data-ioc"
DEFAULT_IOC_TAXONOMY_DIR = "ioc"
VERSION_FILE_NAME = "version.json"

class IocWbl (object):
    """Representation of IOC World Bird List"""

    def __init__ (self):
        self.taxonomy = []
        self.index = {}
        self.version = None
        self.stats = {'infraclass_count': 0,
                      'order_count': 0,
                      'family_count': 0,
                      'genus_count': 0,
                      'species_count': 0,
                      'subspecies_count': 0}

def write_taxon_to_file (directory, taxon):
    """Write the JSON representation of 'taxon' to file."""
    for subtaxon in taxon['subtaxa']:
        write_taxon_to_file (directory, subtaxon)
    if taxon['rank'] == "Species":
        fname = taxon['binomial_name'].replace (" ", "_") + ".json"
    elif taxon['rank'] == "Subspecies":
        fname = taxon['trinomial_name'].replace (" ", "_") + ".json"
    else:
        fname = taxon['name'] + ".json"
    # We save the filenames of the subtaxa in the attribute 'subtaxa'
    subtaxa_files = []
    for subtaxon in taxon['subtaxa']:
        if subtaxon['rank'] == "Species":
            subtaxa_files.append (subtaxon['binomial_name'].replace (" ", "_") + ".json")
        elif subtaxon['rank'] == "Subspecies":
            subtaxa_files.append (subtaxon['trinomial_name'].replace (" ", "_") + ".json")
        else:
            subtaxa_files.append (subtaxon['name'] + ".json")
    taxon['subtaxa'] = subtaxa_files
    f = open (os.path.join (directory, fname), 'w')
    f.write (json.dumps (taxon))
    f.close ()

def write_taxonomy_to_files (iocwbl, verbose):
    """Write JSON representations of the taxa in the master taxonomy to files."""
    p = os.path.join (DEFAULT_IOC_DIR, DEFAULT_IOC_TAXONOMY_DIR)
    if verbose:
        print ("Writing to files ...")
    if os.path.exists (p):
        print ("Error: Directory '%s' already exists." % (p))
        sys.exit (ERROR_DATA_DIR_EXISTS_ALREADY)
    else:
        os.makedirs (p)
    f = open (os.path.join (p, VERSION_FILE_NAME), 'w')
    v = {"version": iocwbl.version}
    f.write (json.dumps (v))
    f.close ()
    for taxon in iocwbl.taxonomy:
        write_taxon_to_file (p, taxon)

def load_ioc_subtaxa (iocwbl, taxon, ioc_dir):
    """Load the subtaxa for the given taxon."""
    i = 0
    for name in taxon['subtaxa']:
        f = open (os.path.join (ioc_dir, name))
        t = json.load (f)
        f.close ()
        taxon['subtaxa'][i] = t
        if t['rank'] == "Order":
            iocwbl.stats['order_count'] += 1
        elif t['rank'] == "Family":
            iocwbl.stats['family_count'] += 1
        elif t['rank'] == "Genus":
            iocwbl.stats['genus_count'] += 1
        elif t['rank'] == "Species":
            iocwbl.stats['species_count'] += 1
        elif t['rank'] == "Subspecies":
            iocwbl.stats['subspecies_count'] += 1
        load_ioc_subtaxa (iocwbl, t, ioc_dir)
        i += 1

def load_ioc_taxonomy (iocwbl, ioc_dir, verbose):
    """Load IOC taxonomy from files."""
    # Read version
    p = os.path.join (DEFAULT_IOC_DIR, DEFAULT_IOC_TAXONOMY_DIR)
    f = open (os.path.join (p, VERSION_FILE_NAME))
    iocwbl.version = json.load (f)["version"]
    f.close ()
    # Read infraclasses:
    p = os.popen ("grep -l '\"rank\": \"Infraclass\"' %s/*.json" % (ioc_dir))
    filenames = p.read ().split ()
    p.close ()
    for fname in filenames:
        f = open (fname)
        taxon = json.load (f)
        f.close ()
        iocwbl.taxonomy.append (taxon)
        load_ioc_subtaxa (iocwbl, taxon, ioc_dir)
        iocwbl.stats['infraclass_count'] += 1

def add_taxonomies (iocwbl, iocplf):
    """Add other taxonomies based on the IOC Other Lists File 'iocolf'."""
    # TBD! We probably need to store the data we read from the iocwlb
    # as a list of "lines"/"entries" each containing information on a taxa,
    # maybe complementing it with an index of taxon names pointing to the
    # corresponding "line"/"entry".

def add_languages (iocwbl, iocmlf):
    """Add languages from the IOC Multilingual file 'iocmlf' to the 'iocwbl'."""
    for name in iter (iocwbl.index):
        if name in iocmlf.taxonomy:
            iocwbl.index[name]["common_names"].update (iocmlf.taxonomy[name])

def add_complementary_info (iocwbl, ioccf):
    """Add complementary information from the IOC Complementary file 'ioccf'."""
    for name in iter (iocwbl.index):
        if name in ioccf.taxonomy and iocwbl.index[name]["rank"] in ["Genus", "Species", "Subspecies"]:
            iocwbl.index[name]["extinct"] = ioccf.taxonomy[name]["extinct"]
            iocwbl.index[name]["code"] = ioccf.taxonomy[name]["code"]
            if iocwbl.index[name]["comment"] != ioccf.taxonomy[name]["comment"]:
                print (name)
                print (" comment: '%s'" % (iocwbl.index[name]["comment"]))
                print (" comment: '%s'" % (ioccf.index[name]["comment"]))

def print_to_stdout (iocwbl, verbose):
    """Print JSON representations to stdout."""
    if verbose:
        print ("Printing to stdout ...")
    print (json.dumps (iocwbl.taxonomy, indent=2))

def print_taxonomy_info (iocwbl, verbose):
    """Print info on IOC taxonomy to stdout."""
    print ("Taxonomy statistics:")
    print ("  Taxonomy: IOC %s" % (iocwbl.version))
    print ("  Infraclasses: %d" % (iocwbl.stats['infraclass_count']))
    print ("  Orders: %d" % (iocwbl.stats['order_count']))
    print ("  Families: %d" % (iocwbl.stats['family_count']))
    print ("  Genus: %d" % (iocwbl.stats['genus_count']))
    print ("  Species: %d" % (iocwbl.stats['species_count']))
    print ("  Subspecies: %d" % (iocwbl.stats['subspecies_count']))
    print ("  Total number of taxa: %d" % (iocwbl.stats['infraclass_count'] +
                                           iocwbl.stats['family_count'] +
                                           iocwbl.stats['order_count'] +
                                           iocwbl.stats['genus_count'] +
                                           iocwbl.stats['species_count'] +
                                           iocwbl.stats['subspecies_count']))

def handle_files (filepaths, write, info, verbose):
    """Handle the IOC files. if 'write' then write data to files. If 'info'
       then print information on the contents of the files. If 'verbose'
       then print information on progress and what's happening."""
    iocwbl = IocWbl ()
    ioc_files = sorted_ioc_files (filepaths)
    ioc_dir = os.path.join (DEFAULT_IOC_DIR, DEFAULT_IOC_TAXONOMY_DIR)
    # First handle the IOC Master file or read existing data from JSON files
    if len (ioc_files) == 0 or not type (ioc_files[0]) == IocMasterFile:
        if not os.path.exists (ioc_dir):
            print ("Error: No master data in '%s' and no IOC Master File to read." % (ioc_dir))
            sys.exit (ERROR_NO_MASTER_DATA)
        elif verbose:
            print ("Loading existing master data from '%s' ..." % (ioc_dir))
        load_ioc_taxonomy (iocwbl, ioc_dir, verbose)
        if verbose:
            print ("IOC Version: %s" % (iocwbl.version))
    elif type (ioc_files[0]) == IocMasterFile:
        if verbose:
            print ("Reading IOC Master File %s ..." % (ioc_files[0].path))
            print ("IOC Version: %s" % (ioc_files[0].version))
        ioc_files[0].read ()
        iocwbl.taxonomy = ioc_files[0].taxonomy
        iocwbl.index = ioc_files[0].index
        iocwbl.stats = ioc_files[0].taxonomy_stats
        iocwbl.version = ioc_files[0].version
    # Now read and handle the rest of the files in the correct order.
    for ioc_file in ioc_files[1:]:
        if type (ioc_file) == IocOtherListsFile:
            if verbose:
                print ("Reading IOC Other Lists file '%s' ..." % (ioc_file))
            ioc_file.read ()
            add_taxonomies (iocwbl, ioc_file)
        elif type (ioc_file) == IocMultilingualFile:
            if verbose:
                print ("Reading IOC Multilingual file '%s' ..." % (ioc_file))
            ioc_file.read ()
            add_languages (iocwbl, ioc_file)
        elif type (ioc_file) == IocComplementaryFile:
            if verbose:
                print ("Reading IOC Complementary file '%s' ..." % (ioc_file))
            ioc_file.read ()
            add_complementary_info (iocwbl, ioc_file)
    if write:
        write_taxonomy_to_files (iocwbl, verbose)
    else:
        print_to_stdout (iocwbl, verbose)
    if info:
        print_taxonomy_info (iocwbl, verbose)

def main():
    parser = argparse.ArgumentParser (description='Read IOC World Bird List\
                                      files and print JSON representations of\
                                      the contents to stdout or to files. If\
                                      the -w option is not chosen it will print\
                                      to stdout.')
    parser.add_argument ('-v', '--verbose', action='store_true', default=False,
                         help="print info about what's going on [False]")
    parser.add_argument ('-i', '--info', action='store_true', default=False,
                         help="print info about the IOC files [False]")
    parser.add_argument ('-w', '--write', action='store_true', default=False,
                         help="write to JSON files [False]")
    parser.add_argument ('ioc_files', nargs='*', help="IOC file(s) to read")
    args = parser.parse_args ()
    # First check if all files exist
    for file in args.ioc_files:
        if not os.path.isfile (file):
            print ("Error: File '%s' not found." % (file))
            sys.exit (ERROR_FILE_NOT_FOUND)
    # Then read the files in correct order
    handle_files (args.ioc_files, args.write, args.info, args.verbose)

if __name__ == "__main__":
    main()
