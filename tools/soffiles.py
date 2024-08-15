#!/usr/bin/env python3

"""This module contains methods and classes for reading SOF files. Currently only one file."""

import json
import os
import os.path
import openpyxl.reader.excel as xlxs
import re


class InvalidSofFile (Exception):
    pass


class UnrecognizedSofFile (Exception):
    pass


class UnrecognizedTaxon (Exception):
    pass


def _is_sof_names_wb(wb):
    """True if 'wb' is an SOF Swedish Names Excel workbook, otherwise False."""
    return wb.worksheets[0].title[0:2] == "NL"


def _sof_wb_version(wb):
    """Returns the SOF version number of the workbook. Returns None if not able to establish
       the version."""
    if _is_sof_names_wb(wb):
        return wb.worksheets[0].title[2:].strip()
    else:
        return None


def sof_file(filepath):
    """Returns a SOF File Names class instance, based om `filepath`."""
    result = None
    try:
        # The values of the cells in the second column titled 'Nivå' are formulas. We want those to
        # be evaluated, so we set `data_only=True` to get the evaluated values, and not the formula
        # itself. See: https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html
        wb = xlxs.load_workbook(filepath, data_only=True)
    except xlxs.InvalidFileException:
        print(f"Error: {filepath} is not an Excel file (.xlxs).")
        raise
    if _is_sof_names_wb(wb):
        result = SofNamesFile(wb, filepath)
    else:
        print(f"Error: {filepath} is not an recognized IOC file.")
        raise UnrecognizedSofFile(filepath)
    return result


class SofNamesFile (object):
    """Represents a SOF Names Master file (Excel)."""

    def __init__(self, workbook, path):
        """Initialize with Excel 'workbook'."""
        self.order = 1
        self.workbook = workbook
        self.path = path
        self.version = None
        self.taxonomy = []        # This list contains the list of top level
                                  # taxa. Each taxa has a 'subtaxa' attribute
                                  # which is a list of taxa, etc.
        self.index = {}           # This index contains all taxa keyed by name
        self.taxonomy_stats = {}
        if _is_sof_names_wb(self.workbook):
            self.version = self.version = _sof_wb_version(self.workbook)
        else:
            print(f"Error: '{path}' is not a valid SOF Names File.\nA SOF Names file must have the text 'NL' in the title of the first worksheet.")
            raise InvalidSofFile(self.path)

    def read(self):
        """Read the taxonomy names data into the attribute 'self.taxonomy' and
           save statistics in the attribute 'self.taxonomy_stats'."""
        self.taxonomy_stats = {'order_count': 0,
                               'family_count': 0,
                               'species_count': 0}
        ws = self.workbook.worksheets[0]
        # First we read all the taxa
        i = 1
        parsing_notes = False
        notes = {}
        taxa_with_notes = []
        for row in ws.iter_rows(min_row=2):
            if not parsing_notes:
                if row[1].value == "ordning":
                    self.taxonomy_stats['order_count'] += 1
                    order = row[2].value
                    taxon = {'rank': 'Order',
                             'name': order,
                             'notes': str(row[5].value).split(),
                             'common_names': {'sv': row[4].value},
                             'subtaxa': []}
                    self.taxonomy.append(taxon)
                elif row[1].value == "familj":
                    self.taxonomy_stats['family_count'] += 1
                    family = row[2].value
                    taxon = {'rank': 'Family',
                             'name': family,
                             'notes': str(row[5].value).split(),
                             'common_names': {'en': row[3].value,
                                              'sv': row[4].value},
                             'subtaxa': []}
                    taxon['supertaxon'] = self.taxonomy[-1]['name']
                    self.taxonomy[-1]['subtaxa'].append(taxon)
                elif row[1].value == "art":
                    self.taxonomy_stats['species_count'] += 1
                    print(row[2].value)
                    taxon = {'rank': 'Species',
                             'binomial_name': row[2].value,
                             'name': row[2].value.split()[1],
                             'notes': str(row[5].value).split(),
                             'common_names': {'en': row[3].value,
                                              'sv': row[4].value},
                             'subtaxa': []}
                    taxon['supertaxon'] = self.taxonomy[-1]['subtaxa'][-1]['name']
                    self.taxonomy[-1]['subtaxa'][-1]['subtaxa'].append(taxon)
                elif row[1].value is None:
                    parsing_notes = True
                else:
                    print(f"Error: Unrecognized taxon type in {self.path} on row {i}: {row[2].value}")
                    raise UnrecognizedTaxon(self.path)
                i += 1
                if len(taxon['notes']) > 0 and not taxon['notes'] == ['None']:
                    taxa_with_notes.append(taxon)
            else:  # parsing_notes
                # First check if we are done reading notes
                if len(notes) > 0 and row[2].value is None:
                    break
                if not row[2].value == "Noter":
                    note_id, note = row[2].value.split(" ", 1)
                    notes[note_id] = note

        # Then we update note attribute of all taxa with the actual notes
        for taxon in taxa_with_notes:
            x = []
            for noteid in taxon['notes']:
                x.append(notes[noteid])
            taxon['notes'] = x


class IocData (object):
    """Represents all IOC data and the entire IOC taxonomic hierarchy. The top
       level taxa are available in the attribute 'top_taxa'. ALl other taxa can
       be retrieved by name with the feature 'taxon'."""

    def __init__(self, directory):
        """Initialize with the specified 'directory'."""
        assert os.path.exists(directory)
        assert os.path.isdir(directory)
        self.directory = directory
        self.top_taxa = self.__top_taxa__()

    def __top_taxa__(self):
        """A list of the top IocTaxon in IOC. These IocTaxa have the rank
           "Infraclass"."""
        result = []
        for name in TOP_TAXA_NAMES:
            result.append(IocTaxon(name))
        return result

    def taxon(self, name):
        """Return the IocTaxon with the given 'name'. Returns None if there is
           no such IocTaxon."""
        t = IocTaxon(name, self.directory)
        if t.exists:
            return t
        else:
            return None


class IocTaxon (object):
    """Represents an IOC taxon as transformed from the Excel data in the IOC
       Master file, Complementary file, Multilingual file and Other Lists
       file. All data for the taxon is available in the attribute 'data'."""

    def __init__(self, name, directory):
        """Initialize with the name, that can be a binomial species or a
           trinomial subspecies name."""
        self.data = {'name': name}
        self.filename = os.path.join(directory, name + '.json')
        self.exists = os.path.exists(self.filename)
        self.__load__()

    def __load__(self):
        """Load from JSON file."""
        if self.exists:
            fname = self.data['name'] + '.json'
            f = open(fname)
            self.data = json.load(f)
            f.close()
