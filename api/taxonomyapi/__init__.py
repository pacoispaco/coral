from flask import Flask

API_NAME = 'twitchspot-api'

app = Flask(API_NAME)

import taxonomyapi.routes
