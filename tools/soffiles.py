#!/usr/bin/env python3

"""This module contains methods and classes for reading SOF files. Currently only one file."""

import json
import os
import os.path
import openpyxl.reader.excel as xlxs


VERSION_FILE_NAME = "version.json"


# Exceptions

class InvalidSofFile (Exception):
    pass


class SofWblDirectoryNotFound(Exception):
    pass


class UnrecognizedSofFile (Exception):
    pass


class UnrecognizedTaxon (Exception):
    pass


# Classes

class SofWbl(object):
    """Representation of SOF World Bird List"""

    def __init__(self, dirpath=None):
        """Initailize the SOF World Bird List. If `dirpath`is None, and empty object will be
           created. If `dirpath` is not None, it will try to read the SOF World Bird List
           JSON-files from there. That assumes that the SOF Name List file has been read and
           the corresponding SOF World Bird List JSON-files have been created at an earlier
           point in time."""
        self.taxonomy = []
        self.index = {}
        self.version = None
        self.stats = {'order_count': 0,
                      'family_count': 0,
                      'species_count': 0}
        if dirpath:
            if os.path.exists(dirpath):
                self.load_taxonomy(dirpath, version_file_name=VERSION_FILE_NAME)
            else:
                print(f"Error: SOF World Bird List directory {dirpath} not found.")
                raise SofWblDirectoryNotFound(dirpath)

    def _write_taxon_to_file(self, directory, taxon):
        """Write the JSON representation of 'taxon' to file."""
        for subtaxon in taxon['subtaxa']:
            self._write_taxon_to_file(directory, subtaxon)
        if taxon['rank'] == "Species":
            fname = taxon['binomial_name'].replace(" ", "_") + ".json"
        else:  # Order or family
            fname = taxon['name'] + ".json"
        subtaxa_files = []
        for subtaxon in taxon['subtaxa']:
            if subtaxon['rank'] == "Species":
                subtaxa_files.append(subtaxon['binomial_name'].replace(" ", "_") + ".json")
            else:  # Order or family
                subtaxa_files.append(subtaxon['name'] + ".json")
        taxon['subtaxa'] = subtaxa_files
        f = open(os.path.join(directory, fname), 'w')
        f.write(json.dumps(taxon))
        f.close()

    def write_to_files(self, dirpath, version_file_name=VERSION_FILE_NAME):
        """Write JSON representations of the taxa in SOF taxonomy to files in the directory
           `dirpath`."""
        assert os.path.exists(dirpath)
        f = open(os.path.join(dirpath, version_file_name), 'w')
        v = {"version": self.version}
        f.write(json.dumps(v))
        f.close()
        for taxon in self.taxonomy:
            self._write_taxon_to_file(dirpath, taxon)

    def _load_subtaxa(self, taxon, dirpath):
        """Load the subtaxa for the given taxon."""
        i = 0
        for name in taxon['subtaxa']:
            f = open(os.path.join(dirpath, name))
            t = json.load(f)
            f.close()
            taxon['subtaxa'][i] = t
            if t['rank'] == "Order":
                self.index[t['name']] = t
                self.stats['order_count'] += 1
            elif t['rank'] == "Family":
                self.index[t['name']] = t
                self.stats['family_count'] += 1
            elif t['rank'] == "Species":
                self.index[t['binomial_name']] = t
                self.stats['species_count'] += 1
            self._load_subtaxa(t, dirpath)
            i += 1

    def load_taxonomy(self, dirpath, version_file_name=VERSION_FILE_NAME):
        """Load SOF taxonomy from files in the directory `dirpath`."""
        # Read version
        f = open(os.path.join(dirpath, version_file_name))
        self.version = json.load(f)["version"]
        f.close()
        # Read orders:
        p = os.popen("grep -l '\"rank\": \"Order\"' %s/*.json" % (dirpath))
        filenames = p.read().split()
        p.close()
        for fname in filenames:
            f = open(fname)
            taxon = json.load(f)
            f.close()
            self.index[taxon['name']] = taxon
            self.taxonomy.append(taxon)
            self._load_subtaxa(taxon, dirpath)
            self.stats['order_count'] += 1


class SofNamesFile (object):
    """Represents a SOF Names Master file (Excel)."""

    def __init__(self, filepath):
        """Initialize with Excel file `filepath`. This will not read the contents of the file."""
        # Check that it is an Excel-file.
        try:
            # The values of the cells in the second column titled 'Nivå' are formulas. We want those
            # to be evaluated, so we set `data_only=True` to get the evaluated values, and not the
            # formula itself.
            # See: https://openpyxl.readthedocs.io/en/stable/api/openpyxl.reader.excel.html
            wb = xlxs.load_workbook(filepath, data_only=True)
        except xlxs.InvalidFileException:
            print(f"Error: {filepath} is not an Excel file (.xlxs).")
            raise
        # Check that it is a SOF Names file, and if so initialize it.
        if self._is_sof_names_wb(wb):
            self.workbook = wb
            self.path = filepath
            self.sofwbl = SofWbl()
            self.version = self._sof_wb_version(self.workbook)
        else:
            print((f"Error: '{filepath}' is not a valid SOF Names File.\nA SOF Names file must "
                   "have the text 'NL' in the title of the first worksheet."))
            raise InvalidSofFile(self.path)

    def _is_sof_names_wb(self, wb):
        """True if 'wb' is an SOF Swedish Names Excel workbook, otherwise False."""
        return wb.worksheets[0].title[0:2] == "NL"

    def _sof_wb_version(self, wb):
        """Returns the SOF version number of the workbook. Returns None if not able to establish
           the version."""
        if self._is_sof_names_wb(wb):
            return wb.worksheets[0].title[2:].strip()
        else:
            return None

    def read(self):
        """Read the taxonomy names data into the attribute 'self.taxonomy' and
           save statistics in the attribute 'self.taxonomy_stats'."""
        ws = self.workbook.worksheets[0]
        # First we read all the taxa
        i = 1
        # The file contains notes in the last rows of the file, and we parse them in the end.
        parsing_notes = False
        notes = {}
        taxa_with_notes = []
        for row in ws.iter_rows(min_row=2):
            if not parsing_notes:
                if row[1].value == "ordning":
                    self.sofwbl.stats['order_count'] += 1
                    order = row[2].value
                    taxon = {'rank': 'Order',
                             'name': order,
                             'notes': str(row[5].value).split(),
                             'common_names': {'sv': row[4].value},
                             'subtaxa': []}
                    self.sofwbl.taxonomy.append(taxon)
                    familj_i = 1
                elif row[1].value == "familj":
                    self.sofwbl.stats['family_count'] += 1
                    family = row[2].value
                    taxon = {'rank': 'Family',
                             'name': family,
                             'notes': str(row[5].value).split(),
                             'common_names': {'en': row[3].value,
                                              'sv': row[4].value},
                             'subtaxa': []}
                    taxon['supertaxon'] = self.sofwbl.taxonomy[-1]['name']
                    taxon['sort_index'] = familj_i
                    familj_i += 1
                    self.sofwbl.taxonomy[-1]['subtaxa'].append(taxon)
                    art_i = 1
                elif row[1].value == "art":
                    self.sofwbl.stats['species_count'] += 1
                    taxon = {'rank': 'Species',
                             'binomial_name': row[2].value,
                             'name': row[2].value.split()[1],
                             'notes': str(row[5].value).split(),
                             'common_names': {'en': row[3].value,
                                              'sv': row[4].value},
                             'subtaxa': []}
                    taxon['supertaxon'] = self.sofwbl.taxonomy[-1]['subtaxa'][-1]['name']
                    taxon['sort_index'] = art_i
                    art_i += 1
                    self.sofwbl.taxonomy[-1]['subtaxa'][-1]['subtaxa'].append(taxon)
                elif row[1].value is None:
                    parsing_notes = True
                else:
                    print((f"Error: Unrecognized taxon type in {self.path} on row {i}: "
                           "{row[2].value}"))
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
