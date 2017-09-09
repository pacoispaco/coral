# Readme for twitchspot-taxonomy

Taxonomy system for Twitchspot. Serves information on biological taxonomies and
species names.

This is part of a personal project that has been going on, with very variable
commitment (!), for around 20 years. The purpose of the project has been to
experiment with both different programming languages and technologies for
manipulating and serving information on biological taxonomies and names, as
well as different solutions for creating checklists and reporting observations.

Twitchspot is the general name of this personal project. This project is a
simpler approach on managing world lists of bird names and providing a simple read
only HTTP API for accessing this information.

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

### Run locally

### Tests

### Directory structure

 * 'data' contains taxonomic data files from external sources
 * 'taxonomyd' contains source code for the HTTP API server
 * 'src' contains source code for various data import and transformation scripts
