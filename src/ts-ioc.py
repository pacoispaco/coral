#!/usr/bin/env python3

# This program reads IOC World Bird List files and prints JSON representations
# of that data to stdout, or to files.

import argparse
import os, os.path, sys
import openpyxl.reader.excel as xlxs
import re
import json
import copy

import pprint

# Constants
ERROR_FILE_NOT_FOUND = 1
ERROR_FILE_NOT_EXCEL = 2
TYPE_IOC_MASTER_FILE = 1
TYPE_IOC_OTHER_LISTS_FILE = 2
TYPE_IOC_MULTILINGUAL_FILE = 3
TYPE_IOC_COMPLEMENTARY_FILE = 4
TYPE_UNRECOGNIZED_FILE = 5
file_types = {TYPE_IOC_MASTER_FILE: "IOC Master file",
              TYPE_IOC_OTHER_LISTS_FILE: "IOC Other lists file",
              TYPE_IOC_MULTILINGUAL_FILE: "IOC Multilingual file",
              TYPE_IOC_COMPLEMENTARY_FILE: "IOC Complementary file",
              TYPE_UNRECOGNIZED_FILE: "Unrecognized file"}
DEFAULT_WRITE_DIR = "./ts_ioc-data"

# Globals
# Object containing representation of file contents
file_contents = {}
# Object containing info on file
file_info = {'infraclass_count': 0,
             'order_count': 0,
             'family_count': 0,
             'genus_count': 0,
             'species_count': 0,
             'subspecies_count': 0}
# IOC taxonomy as parsed from the IOC Master file
taxonomy = []
# IOC taxonomy as parsed from the IOC other lists file
taxonomy_ol = []

def kind_of_ioc_file (workbook):
    """Return a tuple containing of the type and version of IOC file."""
    # We look at which worksheets the workbook contains and their names to
    # deduce the type of IOC file.
    if workbook.worksheets[0].title == "Master":
        s = workbook.worksheets[0].cell (row=1, column=2).value
        regexp = re.compile (".*\((.*)\).*")
        version = regexp.match (s).groups()[0]
        return (TYPE_IOC_MASTER_FILE, version)
    elif "vs_other_lists" in workbook.worksheets[0].title:
        s = workbook.worksheets[0].cell (row=1, column=2).value
        regexp = re.compile (".*\(v (.*)\).*")
        version = regexp.match (s).groups()[0]
        return (TYPE_IOC_OTHER_LISTS_FILE, version)
    elif workbook.worksheets[0].title == "List" and workbook.worksheets[1].title == "Sources":
        s = workbook.worksheets[1].cell (row=1, column=1).value
        regexp = re.compile ("[A-Za-z ]*(\d*\.\d*).*")
        version = regexp.match (s).groups()[0]
        return (TYPE_IOC_MULTILINGUAL_FILE, version)
    elif "IOC" in workbook.worksheets[0].title:
        s = workbook.worksheets[0].title
        regexp = re.compile ("[A-Za-z ]*(\d*\.\d*).*")
        version = regexp.match (s).groups()[0]
        return (TYPE_IOC_COMPLEMENTARY_FILE, version)
    else:
        return (TYPE_UNRECOGNIZED_FILE, None)

def read_ioc_master_file (workbook):
    """Read the IOC Master file workbook."""
    # Note that the global variable 'taxonomy' is a list that will maintain the
    # ordering of taxa in the IOC Master file.
    global taxonomy
    ws = workbook.worksheets[0]
    i = 0
    for row in ws.iter_rows (min_row=5):
        infraclass = row[0].value
        order = row[1].value
        family = row[2].value
        family_en = row[3].value
        genus = row[4].value
        species = row[5].value
        subspecies = row[6].value
        taxon = {'authority': row[7].value,
                 'names': {'en': {'ioc': row[8].value}},
                 'breeding_range': row[9].value,
                 'breeding_subranges': row[10].value,
                 'nonbreeding_range': row[11].value,
                 'code': row[12].value,
                 'comment': row[13].value,
                 'subtaxa': []}
        if infraclass:
            taxon['rank'] = "Infraclass"
            taxon['name'] = infraclass
            taxonomy.append (taxon)
            file_info['infraclass_count'] += 1
        elif order:
            taxon['rank'] = "Order"
            taxon['name'] = order
            taxon['supertaxon'] = taxonomy[-1]['name']
            taxonomy[-1]['subtaxa'].append (taxon)
            file_info['order_count'] += 1
        elif family:
            taxon['rank'] = "Family"
            taxon['name'] = family
            taxon['supertaxon'] = taxonomy[-1]['subtaxa'][-1]['name']
            taxonomy[-1]['subtaxa'][-1]['subtaxa'].append (taxon)
            file_info['family_count'] += 1
        elif genus:
            taxon['rank'] = "Genus"
            taxon['name'] = genus.title ()
            taxon['supertaxon'] = taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['name']
            taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'].append (taxon)
            file_info['genus_count'] += 1
        elif species:
            taxon['rank'] = "Species"
            taxon['name'] = species
            taxon['supertaxon'] = taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['name']
            genus = taxon['supertaxon']
            taxon['binomial_name'] = genus + " " + species
            taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'].append (taxon)
            file_info['species_count'] += 1
        elif subspecies:
            taxon['rank'] = "Subspecies"
            taxon['name'] = subspecies
            taxon['supertaxon'] = taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['name']
            genus = taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['name']
            species = taxon['supertaxon']
            taxon['trinomial_name'] = genus + " " + species + " " + subspecies
            taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'].append (taxon)
            file_info['subspecies_count'] += 1

def read_file (ioc_file, verbose):
    """Read the IOC file."""
    global file_contents, file_info
    if verbose:
        print ("Reading file '%s' ..." % (ioc_file))
    file_info['name'] = ioc_file
    try:
        wb = xlxs.load_workbook (ioc_file)
        # Check what kind of IOC file we have
        file_info['type'], file_info['version'] = kind_of_ioc_file (wb)
        if file_info['type'] == TYPE_IOC_MASTER_FILE:
            read_ioc_master_file (wb)

    except xlxs.InvalidFileException:
        print ("Error: '%s' is not an Excel file (.xlxs)." % (ioc_file))
        sys.exit (ERROR_FILE_NOT_EXCEL)

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
    subtaxa_names = []
    for subtaxon in taxon['subtaxa']:
        if subtaxon['rank'] == "Species":
            subtaxa_names.append (subtaxon['binomial_name'])
        elif subtaxon['rank'] == "Subspecies":
            subtaxa_names.append (subtaxon['trinomial_name'])
        else:
            subtaxa_names.append (subtaxon['name'])
    taxon['subtaxa'] = subtaxa_names
    f = open (os.path.join (directory, fname), 'w')
    f.write (json.dumps (taxon))
    f.close ()

def write_to_files(verbose):
    """Print JSON representations to files."""
    if verbose:
        print ("Writing to files ...")
    if os.path.exists (DEFAULT_WRITE_DIR):
        print ("AError: Directory '%s' already exists." % (DEFAULT_WRITE_DIR))
    else:
        os.makedirs(DEFAULT_WRITE_DIR)
    for taxon in taxonomy:
        write_taxon_to_file (DEFAULT_WRITE_DIR, taxon)

def print_to_stdout (verbose):
    """Print JSON representations to stdout."""
    if verbose:
        print ("Printing to stdout ...")
    print (json.dumps (taxonomy, indent=2))

def print_info (verbose):
    """Print info on IOC file to stdout."""
    if verbose:
        print ("Printing info on '%s' ..." %(file_info['name']))
    print ("File: '%s'" % (file_info['name']))
    print ("Type: %s" % (file_types[file_info['type']]))
    print ("Version: %s" % (file_info['version']))
    print ("Infraclass count: %d" % (file_info['infraclass_count']))
    print ("Order count: %d" % (file_info['order_count']))
    print ("Family count: %d" % (file_info['family_count']))
    print ("Genus count: %d" % (file_info['genus_count']))
    print ("Species count: %d" % (file_info['species_count']))
    print ("Subspecies count: %d" % (file_info['subspecies_count']))

def main():
    parser = argparse.ArgumentParser (description='Read IOC World Bird List\
                                      files and print JSON representations of\
                                      the contents to stdout or to files. If\
                                      the -w option is not chosen it will print\
                                      to stdout.')
    parser.add_argument ('-v', '--verbose', action='store_true', default=False,
                         help="print info about what's going on [False]")
    parser.add_argument ('-i', '--info', action='store_true', default=False,
                         help="print info about the IOC file [False]")
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
    # files = sort_files_according_to_type (args_ioc_files) TBD!
    for file in args.ioc_files:
        read_file (file, args.verbose)
        if args.info:
            print_info (args.verbose)
        elif args.write:
            write_to_files (args.verbose)
        else:
            print_to_stdout (args.verbose)

if __name__ == "__main__":
    main()
