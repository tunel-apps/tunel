#!/bin/bash

# Create a temporary file with modules, echo back
tmpfile=$(mktemp /tmp/tunel-modules.XXXXXX)
ml -t spider 2> $tmpfile
echo "RESULT:${tmpfile}"
