# BirdLife Sweden list of Swedish names

BirdLife Sweden, with the Swedish name Svenska Ornitoligiska Föreningen (SOF), has a taxonomy
committee that maintains a list of the official Swedish names of all the birds of the world. It
is updated as taxonomic changes are introduced and the list quite closely follows the IOC list.

The name list is published on BirdLife Sweden's web site at https://birdlife.se/tk/svenska-namn-pa-varldens-faglar/

The file is published both as a Excel file (.xlxs) and as a PDF file. The deduced format is:

* A single data sheet with the title "NL NN" where NN denotes the version. E.g. "NL 17" for the
  17:th version of the name list file.
* A title row with column headings. Se below for a description of the columns.
* A number of rows for each order, family and species. No subspecies are included. As of 2024-08-14
  and version 17 of the name list, it contained 44 orders, 252 families and 11197 sepcies, totalling
  11493 rows.
* A single row with no data cells
* A number of rows with footnotes, all in the third column.

Each row with data on an order, family or a species has the following columns/cells:

* "Nr". Indicates the item number.
* "Nivå". Indicates if it is an order, family or species data row. It is implemented as an Excel 
  formula for some unknown reason.
* "Vetenskapligt namn". The scientific name.
* "Engelskt nam". The English name.
* "Svenskt namn". The Swedish name.
* "Not". A note that may indicate if the order, family or species is extinct ('†') or a number
  referring to a numbered note in the row of notes at the end of the Excel sheet.

Each row with a footnote, contains the actual footnote with its number in the third column. For
some unknown reason a single footnote may be spilt over two rows. This makes parsing the file a
unnecessarily tricky. So the soffile.py module is simplified to expect one note per row, and you
need to manually concatenate notes over two rows into notes on just one row.