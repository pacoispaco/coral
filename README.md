# Readme for twitchspot-taxonomy

Twitchspot is the name of my personal project for experimenting with different
programming languages and technologies for manipulating and serving information 
on biological taxonomies and names, as well as different solutions for creating
checklists and reporting observations. This has been an ongoing project, with
very varying commitment for around 20 years.

Twitchspot-taxonomy is an HTTP API that serves information on biological
taxonomies and species names. It also comprises a few command line tools for
importing taxonomical data to the system from different sources.

Copyright (C) 1998-2017 Paul Cohen.
This software is licensed under the GNU Affero General Public License version 3.
See the file [agpl.md](agpl.md) in this directory.

## Development

### Requirements

 * Python 3 & virtualenv.
 * Flask
 * Docker for running the HTTP API server.

### Setup development

Set up a Python virtualenv in the top directory of this project:
```bash
$ virtualenv env
```

Jump into to the virtualenv and install required Python modules:
```bash
$ source env/bin/activate
(env) $ pip install -r requirements.txt
```

### Build

TBD.

### Run locally

TBD.

### Tests

TBD.

### Directory structure

 * 'data' contains taxonomic data files from external sources
 * 'taxonomyd' contains source code for the HTTP API server
 * 'src' contains source code for various data import and transformation scripts
