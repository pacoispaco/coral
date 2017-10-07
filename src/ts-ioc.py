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

# Error constants
ERROR_FILE_NOT_FOUND = 1
ERROR_FILE_NOT_EXCEL = 2
ERROR_DATA_DIR_EXISTS_ALREADY = 3
ERROR_NO_MASTER_DATA = 4
ERROR_INCONSISTENT_VERSIONS = 5

# File type constants. The value also denotes the order in which these files
# should be read
TYPE_IOC_MASTER_FILE = 1
TYPE_IOC_OTHER_LISTS_FILE = 2
TYPE_IOC_MULTILINGUAL_FILE = 3
TYPE_IOC_COMPLEMENTARY_FILE = 4
TYPE_UNRECOGNIZED_EXCEL_FILE = 5
file_types = {TYPE_IOC_MASTER_FILE: "IOC Master file",
              TYPE_IOC_OTHER_LISTS_FILE: "IOC Other lists file",
              TYPE_IOC_MULTILINGUAL_FILE: "IOC Multilingual file",
              TYPE_IOC_COMPLEMENTARY_FILE: "IOC Complementary file",
              TYPE_UNRECOGNIZED_EXCEL_FILE: "Unrecognized Excel file"}

# Directory and file name constants
DEFAULT_IOC_DIR = "./data-ioc"
VERSION_FILE_NAME = "version.json"

# Globals
# Object containing representation of file contents
file_contents = {}
# Object containing info on file
file_stats = {'infraclass_count': 0,
              'order_count': 0,
              'family_count': 0,
              'genus_count': 0,
              'species_count': 0,
              'subspecies_count': 0}
# IOC taxonomy as parsed from the IOC Master file
master_taxonomy = []
taxonomy_version = None
# IOC taxonomy as parsed from the IOC other lists file
taxonomy_ol = []
ioc_dir = DEFAULT_IOC_DIR

def kind_of_ioc_file (filename):
    """Return an object containing info on the name, type and version of IOC file."""
    # We try to read the 'filename' as an Excel file and then look at which
    # worksheets the workbook contains and their names to deduce the type of
    # IOC file.
    try:
        wb = xlxs.load_workbook (filename)
    except xlxs.InvalidFileException:
        print ("Error: '%s' is not an Excel file (.xlxs)." % (ioc_file))
        sys.exit (ERROR_FILE_NOT_EXCEL)
    if wb.worksheets[0].title == "Master":
        s = wb.worksheets[0].cell (row=1, column=2).value
        regexp = re.compile (".*\((.*)\).*")
        version = regexp.match (s).groups()[0]
        return {'filename': filename,
                'type': TYPE_IOC_MASTER_FILE,
                'version': version}
    elif "vs_other_lists" in wb.worksheets[0].title:
        s = wb.worksheets[0].cell (row=1, column=2).value
        regexp = re.compile (".*\(v (.*)\).*")
        version = regexp.match (s).groups()[0]
        return {'filename': filename,
                'type': TYPE_IOC_OTHER_LISTS_FILE,
                'version': version}
    elif wb.worksheets[0].title == "List" and wb.worksheets[1].title == "Sources":
        s = wb.worksheets[1].cell (row=1, column=1).value
        regexp = re.compile ("[A-Za-z ]*(\d*\.\d*).*")
        version = regexp.match (s).groups()[0]
        return {'filename': filename,
                'type': TYPE_IOC_MULTILINGUAL_FILE,
                'version': version}
    elif "IOC" in wb.worksheets[0].title:
        s = wb.worksheets[0].title
        regexp = re.compile ("[A-Za-z ]*(\d*\.\d*).*")
        version = regexp.match (s).groups()[0]
        return {'filename': filename,
                'type': TYPE_IOC_COMPLEMENTARY_FILE,
                'version': version}
    else:
        return (TYPE_UNRECOGNIZED_EXCEL_FILE, None)

def read_ioc_master_file (filename):
    """Read the IOC Master file workbook."""
    # Note that the global variable 'master_taxonomy' is a list that will maintain the
    # ordering of taxa in the IOC Master file.
    global master_taxonomy
    wb = xlxs.load_workbook (filename)
    ws = wb.worksheets[0]
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
            master_taxonomy.append (taxon)
            file_stats['infraclass_count'] += 1
        elif order:
            taxon['rank'] = "Order"
            taxon['name'] = order
            taxon['supertaxon'] = master_taxonomy[-1]['name']
            master_taxonomy[-1]['subtaxa'].append (taxon)
            file_stats['order_count'] += 1
        elif family:
            taxon['rank'] = "Family"
            taxon['name'] = family
            taxon['supertaxon'] = master_taxonomy[-1]['subtaxa'][-1]['name']
            master_taxonomy[-1]['subtaxa'][-1]['subtaxa'].append (taxon)
            file_stats['family_count'] += 1
        elif genus:
            taxon['rank'] = "Genus"
            taxon['name'] = genus.title ()
            taxon['supertaxon'] = master_taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['name']
            master_taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'].append (taxon)
            file_stats['genus_count'] += 1
        elif species:
            taxon['rank'] = "Species"
            taxon['name'] = species
            taxon['supertaxon'] = master_taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['name']
            genus = taxon['supertaxon']
            taxon['binomial_name'] = genus + " " + species
            master_taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'].append (taxon)
            file_stats['species_count'] += 1
        elif subspecies:
            taxon['rank'] = "Subspecies"
            taxon['name'] = subspecies
            taxon['supertaxon'] = master_taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['name']
            genus = master_taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['name']
            species = taxon['supertaxon']
            taxon['trinomial_name'] = genus + " " + species + " " + subspecies
            master_taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'].append (taxon)
            file_stats['subspecies_count'] += 1

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

def write_master_taxonomy_to_files (version, verbose):
    """Write JSON representations of the taxa in the master taxonomy to files."""
    global taxonomy_version
    if verbose:
        print ("Writing to files ...")
    if os.path.exists (DEFAULT_IOC_DIR):
        print ("Error: Directory '%s' already exists." % (DEFAULT_IOC_DIR))
        sys.exit (ERROR_DATA_DIR_EXISTS_ALREADY)
    else:
        os.makedirs(DEFAULT_IOC_DIR)
    f = open (os.path.join (DEFAULT_IOC_DIR, VERSION_FILE_NAME), 'w')
    v = {"version": version}
    f.write (json.dumps (v))
    f.close ()
    taxonomy_version = version
    for taxon in master_taxonomy:
        write_taxon_to_file (DEFAULT_IOC_DIR, taxon)

def load_ioc_subtaxa (taxon):
    """Load the subtaxa for the given taxon."""
    global master_taxonomy
    i = 0
    for name in taxon['subtaxa']:
        f = open (os.path.join (ioc_dir, name))
        t = json.load (f)
        f.close ()
        taxon['subtaxa'][i] = t
        if t['rank'] == "Order":
            file_stats['order_count'] += 1
        elif t['rank'] == "Family":
            file_stats['family_count'] += 1
        elif t['rank'] == "Genus":
            file_stats['genus_count'] += 1
        elif t['rank'] == "Species":
            file_stats['species_count'] += 1
        elif t['rank'] == "Subspecies":
            file_stats['subspecies_count'] += 1
        load_ioc_subtaxa (t)
        i += 1

def load_ioc_taxonomy (verbose):
    """Load IOC taxonomy from files."""
    global master_taxonomy, master_taxonomy_index, taxonomy_version
    # Read version
    f = open (os.path.join (DEFAULT_IOC_DIR, VERSION_FILE_NAME))
    taxonomy_version = json.load (f)["version"]
    f.close ()
    # Read infraclasses:
    p = os.popen ("grep -l '\"rank\": \"Infraclass\"' %s/*.json" % (ioc_dir))
    filenames = p.read ().split ()
    p.close ()
    for fname in filenames:
        f = open (fname)
        taxon = json.load (f)
        f.close ()
        master_taxonomy.append (taxon)
        load_ioc_subtaxa (taxon)
        file_stats['infraclass_count'] += 1

def print_to_stdout (verbose):
    """Print JSON representations to stdout."""
    if verbose:
        print ("Printing to stdout ...")
    print (json.dumps (master_taxonomy, indent=2))

def print_taxonomy_info (verbose):
    """Print info on IOC taxonomy to stdout."""
    print ("Taxonomy: IOC %s" % (taxonomy_version))
    print ("Infraclasses: %d" % (file_stats['infraclass_count']))
    print ("Orders: %d" % (file_stats['order_count']))
    print ("Families: %d" % (file_stats['family_count']))
    print ("Genus: %d" % (file_stats['genus_count']))
    print ("Species: %d" % (file_stats['species_count']))
    print ("Subspecies: %d" % (file_stats['subspecies_count']))
    print ("Total number of taxa: %d" % (file_stats['infraclass_count'] +
                                         file_stats['family_count'] +
                                         file_stats['order_count'] +
                                         file_stats['genus_count'] +
                                         file_stats['species_count'] +
                                         file_stats['subspecies_count']))

def print_version_info (file_infos):
    """Print version info."""
    print ("Taxonomy version: %s" % (taxonomy_version))
    for x in file_infos:
        print ("File name: '%s', version: %s" % (x["filename"], x["version"]))

def handle_files (file_names, write, info, verbose):
    """Handle the IOC files. if 'write' then write data to files. If 'info'
       then print information on the contents of the files. If 'verbose'
       then print information on progress and what's happening."""
    global file_stats
    # First inspect the files and determine the order to handle them in.
    if verbose:
        print ("Inspecting files ...")
    file_infos = []
    for name in file_names:
        file_infos.append (kind_of_ioc_file (name))
    file_infos = sorted (file_infos, key=lambda file_info: file_info['type'])
    # If we don't have a TYPE_IOC_MASTER_FILE and we don't have any written
    # files to work with, we must abandon, since we don't have any master data.
    if not file_infos or not file_infos[0]['type'] == TYPE_IOC_MASTER_FILE:
        if not os.path.exists (ioc_dir):
            print ("Error: No master data in '%s' and no IOC Master File to read." % (ioc_dir))
            sys.exit (ERROR_NO_MASTER_DATA)
        elif verbose:
            print ("Using existing master data in '%s' ..." % (ioc_dir))
        load_ioc_taxonomy (verbose)
    else:
        # Read and handle the master file
        if verbose:
            print ("Handling the IOC Master file ...")
        read_ioc_master_file (file_infos[0]['filename'])
        if write:
            write_master_taxonomy_to_files (file_infos[0]['version'], verbose)
    # Check that the taxonomy version is the same in all files
    if not all ([x["version"] == file_infos[0]["version"] for x in file_infos]):
        print ("Error: Inconsistent version numbers in files and/or existing taxomy files")
        print_version_info (file_infos)
        sys.exit (ERROR_INCONSISTENT_VERSIONS)
    # Now read and handle the rest of the files in the correct order.
    if verbose:
        print ("Reading other IOC files ...")
    for file_info in file_infos:
        pass
    if write:
        pass
    else:
        print_to_stdout (verbose)
    if info:
        print_taxonomy_info (verbose)

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
