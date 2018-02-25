"""Module containing functions for handling requests to Taxonomy API URL:s."""

import json

from taxonomyapi import app

@app.route('/')
def root():
    """Returns the API (root) resource."""
    return json.dumps ({'name': 'Twitchspot Taxonomy HTTP API',
                        'upgraded': '2018-01-10 15:43.34',
                        'updated': '2018-01-10 15:44.12',
                        'links': []})

@app.route('/sources')
def sources():
    """Returns data sources."""
    return json.dumps ({'name': 'Twitchspot Taxonomy Data Sources'})

@app.route('/taxa')
def taxa():
    """Returns taxa."""
    return json.dumps ({'name': 'Twitchspot Taxonomy Taxa'})
