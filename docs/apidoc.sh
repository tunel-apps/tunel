#!/bin/bash
# If the modules changed, the content of "source" should be backed up and
# new files generated (to update) by doing:
#
# 
rm api_reference/tunel.*
sphinx-apidoc -o api_reference/ ../tunel
