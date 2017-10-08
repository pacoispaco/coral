#!/usr/bin/env python3

"""This module contains methods and classes for reading IOC files."""

import os, os.path
import openpyxl.reader.excel as xlxs
import re

class InvalidIocMasterFile (Exception):
    pass

class InvalidIocOtherListsFile (Exception):
    pass

class InvalidIocMultilingualFile (Exception):
    pass

class InvalidIocComplementaryFile (Exception):
    pass

class UnrecognizedIocFile (Exception):
    pass

class MultipleIocFilesOfSameType (Exception):
    pass

class MultipleVersionsOfIocFiles (Exception):
    pass

def sorted_ioc_files (filepaths):
    """Returns a list of IOC File class instances sorted in the order they
       should be processed."""
    result = []
    for path in filepaths:
        try:
            wb = xlxs.load_workbook (path)
        except xlxs.InvalidFileException:
            print ("Error: '%s' is not an Excel file (.xlxs)." % (path))
            raise
        if wb.worksheets[0].title == "Master":
            result.append (IocMasterFile (wb, path))
        elif "vs_other_lists" in wb.worksheets[0].title:
            result.append (IocOtherListsFile (wbi, path))
        elif wb.worksheets[0].title == "List" and wb.worksheets[1].title == "Sources":
            result.append (IocMultilingualFile (wbi, path))
        elif "IOC" in wb.worksheets[0].title:
            result.append (IocComplementaryFile (wbi, path))
        else:
            print ("Error: '%s' is not an recognized IOC file." % (path))
            raise UnrecognizedIocFile (path)
    # Make sure we don't have multiple IOC files of the same type
    orders = [file.order for file in result]
    if not len (set (orders)) == len (orders):
        print ("Error: Multiple IOC files of same type.")
        raise MultipleIocFilesOfSameType (filepaths)
    # Make sure all IOC files have the same version
    versions = [file.version for file in result]
    if not len (set (versions)) == 1:
        print ("Error: Multiple versions of IOC files.")
        raise MultipleVersionsOfIocFiles (filepaths)
    # Return the list of IOC files sorted by their 'order' attribute
    return sorted (result, key=lambda iocfile: iocfile.order)

def is_ioc_master_file (filepath):
    """Return 'True' if 'filepath' is a IOC Master file."""
    assert os.path.isfile (filepath)
    try:
        wb = xlxs.load_workbook (filepath)
    except xlxs.InvalidFileException:
        return False
    if wb.worksheets[0].title == "Master":
        return True
    else:
        return False

class IocMasterFile (object):
    """Represents a IOC Master file."""

    def __init__ (self, workbook, path):
        """Initialize with Excel 'workbook'."""
        self.order = 1
        self.workbook = workbook
        self.path = path
        self.version = None
        self.taxonomy = []
        self.taxonomy_stats = {}
        if self.workbook.worksheets[0].title == "Master":
            s = self.workbook.worksheets[0].cell (row=1, column=2).value
            regexp = re.compile (".*\((.*)\).*")
            self.version = regexp.match (s).groups()[0]
        else:
            print ("Error; '%s' is not a avalid IOC Master File" % (filepath))
            raise InvalidIocMasterFile (filepath)

    def read (self):
        """Read the taxonomy data into the attribute 'self.taxonomy' and
           save statistics in the attribute 'self.taxonomy_stats'."""
        # Note that the global variable 'master_taxonomy' is a list that will maintain the
        # ordering of taxa in the IOC Master file.
        self.taxonomy_stats = {'infraclass_count': 0,
                               'order_count': 0,
                               'family_count': 0,
                               'genus_count': 0,
                               'species_count': 0,
                               'subspecies_count': 0}
        ws = self.workbook.worksheets[0]
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
                self.taxonomy.append (taxon)
                self.taxonomy_stats['infraclass_count'] += 1
            elif order:
                taxon['rank'] = "Order"
                taxon['name'] = order
                taxon['supertaxon'] = self.taxonomy[-1]['name']
                self.taxonomy[-1]['subtaxa'].append (taxon)
                self.taxonomy_stats['order_count'] += 1
            elif family:
                taxon['rank'] = "Family"
                taxon['name'] = family
                taxon['supertaxon'] = self.taxonomy[-1]['subtaxa'][-1]['name']
                self.taxonomy[-1]['subtaxa'][-1]['subtaxa'].append (taxon)
                self.taxonomy_stats['family_count'] += 1
            elif genus:
                taxon['rank'] = "Genus"
                taxon['name'] = genus.title ()
                taxon['supertaxon'] = self.taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['name']
                self.taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'].append (taxon)
                self.taxonomy_stats['genus_count'] += 1
            elif species:
                taxon['rank'] = "Species"
                taxon['name'] = species
                taxon['supertaxon'] = self.taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['name']
                genus = taxon['supertaxon']
                taxon['binomial_name'] = genus + " " + species
                self.taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'].append (taxon)
                self.taxonomy_stats['species_count'] += 1
            elif subspecies:
                taxon['rank'] = "Subspecies"
                taxon['name'] = subspecies
                taxon['supertaxon'] = self.taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['name']
                genus = self.taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['name']
                species = taxon['supertaxon']
                taxon['trinomial_name'] = genus + " " + species + " " + subspecies
                self.taxonomy[-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'][-1]['subtaxa'].append (taxon)
                self.taxonomy_stats['subspecies_count'] += 1

class IocOtherListsFile (object):
    """Represents a IOC Other Lists file."""

    def __init__ (self, workbook, path):
        """Initialize with the Excel 'workbook'."""
        self.order = 2
        self.workbook = workbook
        self.path = path
        self.version = None
        self.taxonomy = []
        self.taxonomy_stats = {}
        if "vs_other_lists" in self.workbook.worksheets[0].title:
            s = self.workbook.worksheets[0].cell (row=1, column=2).value
            regexp = re.compile (".*\(v (.*)\).*")
            self.version = regexp.match (s).groups()[0]
        else:
            print ("Error; '%s' is not a valid IOC Other Lists File" % (filepath))
            raise InvalidIocOtherListsFile (filepath)

    def read (self):
        """Read the taxonomy data into the attribute 'self.taxonomy' and
           save statistics in the attribute 'self.taxonomy_stats'."""
        # Note that the global variable 'master_taxonomy' is a list that will maintain the
        # ordering of taxa in the IOC Master file.
        self.taxonomy_stats = {'infraclass_count': 0,
                               'order_count': 0,
                               'family_count': 0,
                               'genus_count': 0,
                               'species_count': 0,
                               'subspecies_count': 0}

class IocMultilingualFile (object):
    """Represents a IOC Multilingual file."""

    def __init__ (self, workbooki, path):
        """Initialize with the Excel 'workbook'."""
        self.order = 3
        self.workbook= workbook
        self.path = path
        self.version = None
        self.taxonomy = []
        self.taxonomy_stats = {}
        if self.workbook.worksheets[0].title == "List" and self.workbook.worksheets[1].title == "Sources":
            s = self.workbook.worksheets[1].cell (row=1, column=1).value
            regexp = re.compile ("[A-Za-z ]*(\d*\.\d*).*")
            self.version = regexp.match (s).groups()[0]
        else:
            print ("Error; '%s' is not a valid IOC Multilingual File" % (filepath))
            raise InvalidIocMultilingualFile (filepath)

    def read (self):
        """Read the taxonomy data into the attribute 'self.taxonomy' and
           save statistics in the attribute 'self.taxonomy_stats'."""
        # Note that the global variable 'master_taxonomy' is a list that will maintain the
        # ordering of taxa in the IOC Master file.
        self.taxonomy_stats = {'infraclass_count': 0,
                               'order_count': 0,
                               'family_count': 0,
                               'genus_count': 0,
                               'species_count': 0,
                               'subspecies_count': 0}

class IocComplementaryFile (object):
    """Represents a IOC COmplementary file."""

    def __init__ (self, workbook, path):
        """Initialize with the Excel 'workbook'."""
        self.order = 4
        self.workbook= workbook
        self.path = path
        self.version = None
        self.taxonomy = []
        self.taxonomy_stats = {}
        if "IOC" in self.workbook.worksheets[0].title:
            s = self.workbook.worksheets[0].title
            regexp = re.compile ("[A-Za-z ]*(\d*\.\d*).*")
            self.version = regexp.match (s).groups()[0]
        else:
            print ("Error; '%s' is not a valid IOC Complementary File" % (filepath))
            raise InvalidIocComplemntaryFile (filepath)

    def read (self):
        """Read the taxonomy data into the attribute 'self.taxonomy' and
           save statistics in the attribute 'self.taxonomy_stats'."""
        # Note that the global variable 'master_taxonomy' is a list that will maintain the
        # ordering of taxa in the IOC Master file.
        self.taxonomy_stats = {'infraclass_count': 0,
                               'order_count': 0,
                               'family_count': 0,
                               'genus_count': 0,
                               'species_count': 0,
                               'subspecies_count': 0}


