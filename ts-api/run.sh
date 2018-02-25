#!/bin/bash

# Run the API in Flask standalone mode for test, debug purposes etc.

if [[ "$VIRTUAL_ENV" != "" ]]
then
  # Add '.' to PYTHONPATH since the app is a Python package/directory
  export PYTHONPATH=$PYTHONPATH:.
  export FLASK_APP=taxonomyapi
  export FLASK_DEBUG=1
  flask run -p 5005
else
  echo "Failed to run API as standalone Flask application.
Not running in a virtual environment. Make sure to run:
$ source env/bin/activate
in the root directory of this project."
fi
