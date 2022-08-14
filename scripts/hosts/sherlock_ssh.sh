#!/bin/bash
#
# Sherlock cluster at Stanford
# Prints an ssh configuration for the user, selecting a login node at random
# Sample usage: bash sherlock_ssh.sh
echo
read -p "Sherlock username > "  TUNEL_USERNAME

echo "Host sherlock
    User ${TUNEL_USERNAME}
    Hostname login.sherlock.stanford.edu
    GSSAPIDelegateCredentials yes
    GSSAPIAuthentication yes
    ControlMaster auto
    ControlPersist yes
    ControlPath ~/.ssh/%C"
