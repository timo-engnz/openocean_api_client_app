#!/bin/bash

if [ "$MODULE" == "flaskApp" ]; then
    flask run
else
  python -m $MODULE
fi

