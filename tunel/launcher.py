__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from tunel.logger import logger
import tunel.utils as utils
import tunel.ssh
import os


class Launcher:
    """
    A launcher is a base for executing commands.
    """

    def __init__(self, server, **kwargs):
        """
        The Launcher is not responsible for managing or closing the connection.
        """
        self.ssh = tunel.ssh.Tunnel(server, **kwargs)
        self.home = None

    def __str__(self):
        return str(self.__class__.__name__)

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def init_tunel(self):
        """
        Init tunel, meaning creating a directory structure in $HOME, but only
        if the launcher needs to save some kind of state. Otherwise, not needed.
        This is recommended to be run on the init of a launcher or during run.
        """
        if not self.home:
            self.home = self.ssh.execute_or_fail(
                "echo %s" % self.ssh.settings.tunel_home
            )[-1].strip()
            self.ssh.execute_or_fail("mkdir -p %s" % os.path.join(self.home, "tunel"))


class Slurm(Launcher):
    """
    A slurm launcher interacts with slurm
    """

    pass


class Singularity(Launcher):

    # TODO what about exec?
    def run(self, *args, **kwargs):
        res = self.ssh.execute("singularity exec %s" % " ".join(args[0]))
        self.ssh.print_output(res)


"""    
#!/bin/bash
#
# Starts a remote sbatch jobs and sets up correct port forwarding.
# Sample usage: bash start.sh sherlock/singularity-jupyter 
#               bash start.sh sherlock/singularity-jupyter /home/users/raphtown
#               bash start.sh sherlock/singularity-jupyter /home/users/raphtown

if [ ! -f params.sh ]
then
    echo "Need to configure params before first run, run setup.sh!"
    exit
fi
. params.sh

if [ "$#" -eq 0 ]
then
    echo "Need to give name of sbatch job to run!"
    exit
fi

if [ ! -f helpers.sh ]
then
    echo "Cannot find helpers.sh script!"
    exit
fi
. helpers.sh

NAME="${1:-}"

# The user could request either <resource>/<script>.sbatch or
#                               <name>.sbatch
SBATCH="$NAME.sbatch"

# set FORWARD_SCRIPT and FOUND
set_forward_script
check_previous_submit


echo
echo "== Uploading sbatch script =="
scp $FORWARD_SCRIPT ${RESOURCE}:$RESOURCE_HOME/forward-util/

# adjust PARTITION if necessary
set_partition
echo

echo "== Submitting sbatch =="

SBATCH_NAME=$(basename $SBATCH)
command="sbatch
    --job-name=$NAME
    --partition=$PARTITION
    --output=$RESOURCE_HOME/forward-util/$SBATCH_NAME.out
    --error=$RESOURCE_HOME/forward-util/$SBATCH_NAME.err
    --mem=$MEM
    --time=$TIME
    $RESOURCE_HOME/forward-util/$SBATCH_NAME $PORT \"${@:2}\""

echo ${command}
ssh ${RESOURCE} ${command}

# Tell the user how to debug before trying
instruction_get_logs

# Wait for the node allocation, get identifier
get_machine
echo "notebook running on $MACHINE"

setup_port_forwarding

sleep 10
echo "== Connecting to notebook =="

# Print logs for the user, in case needed
print_logs

echo
instruction_get_logs

echo 
echo "== Instructions =="
echo "1. Password, output, and error printed to this terminal? Look at logs (see instruction above)"
echo "2. Browser: http://$MACHINE:$PORT/ -> http://localhost:$PORT/..."
echo "3. To end session: bash end.sh ${NAME}"


#!/bin/bash
#
# Helper Functions shared between forward tool scripts

#
# Configuration
#

function set_forward_script() {

    FOUND="no"
    echo "== Finding Script =="

    declare -a FORWARD_SCRIPTS=("sbatches/${RESOURCE}/$SBATCH" 
                                "sbatches/$SBATCH"
                                "${RESOURCE}/$SBATCH" 
                                "$SBATCH");

    for FORWARD_SCRIPT in "${FORWARD_SCRIPTS[@]}"
    do
        echo "Looking for ${FORWARD_SCRIPT}";
        if [ -f "${FORWARD_SCRIPT}" ]
            then
            FOUND="${FORWARD_SCRIPT}"
            echo "Script      ${FORWARD_SCRIPT}";
            break
        fi
    done
    echo

    if [ "${FOUND}" == "no" ]
    then
        echo "sbatch script not found!!";
        echo "Make sure \$RESOURCE is defined" ;
        echo "and that your sbatch script exists in the sbatches folder.";
        exit
    fi

}

#
# Job Manager
#

function check_previous_submit() {

    echo "== Checking for previous notebook =="
    PREVIOUS=`ssh ${RESOURCE} squeue --name=$NAME --user=$FORWARD_USERNAME -o "%R" -h`
    if [ -z "$PREVIOUS" -a "${PREVIOUS+xxx}" = "xxx" ]; 
        then
            echo "No existing ${NAME} jobs found, continuing..."
        else
        echo "Found existing job for ${NAME}, ${PREVIOUS}."
        echo "Please end.sh before using start.sh, or use resume.sh to resume."
        exit 1
    fi
}


function set_partition() {

    if [ "${PARTITION}" == "gpu" ];
    then
        echo "== Requesting GPU =="
        PARTITION="${PARTITION} --gres gpu:1"
    fi
}

function get_machine() {

    TIMEOUT=${TIMEOUT-1}
    ATTEMPT=0

    echo
    echo "== Waiting for job to start, using exponential backoff =="
    MACHINE=""

    ALLOCATED="no"
    while [[ $ALLOCATED == "no" ]]
      do
                                                                  # nodelist
          MACHINE=`ssh ${RESOURCE} squeue --name=$NAME --user=$FORWARD_USERNAME -o "%N" -h`
    
          if [[ "$MACHINE" != "" ]]
          then
              echo "Attempt ${ATTEMPT}: resources allocated to ${MACHINE}!.."  1>&2
              ALLOCATED="yes"
              break
          fi

        echo "Attempt ${ATTEMPT}: not ready yet... retrying in $TIMEOUT.."  1>&2
        sleep $TIMEOUT

        ATTEMPT=$(( ATTEMPT + 1 ))
        TIMEOUT=$(( TIMEOUT * 2 ))

    done

    echo $MACHINE
    MACHINE="`ssh ${RESOURCE} squeue --name=$NAME --user=$FORWARD_USERNAME -o "%R" -h`"
    echo $MACHINE

    # If we didn't get a node...
    if [[ "$MACHINE" != "$MACHINEPREFIX"* ]]
    then	
        echo "Tried ${ATTEMPTS} attempts!"  1>&2
        exit 1
    fi
}


#
# Instructions
#


function instruction_get_logs() {
    echo
    echo "== View logs in separate terminal =="
    echo "ssh ${RESOURCE} cat $RESOURCE_HOME/forward-util/${SBATCH_NAME}.out"
    echo "ssh ${RESOURCE} cat $RESOURCE_HOME/forward-util/${SBATCH_NAME}.err"
}

function print_logs() {

    ssh ${RESOURCE} cat $RESOURCE_HOME/forward-util/${SBATCH_NAME}.out
    ssh ${RESOURCE} cat $RESOURCE_HOME/forward-util/${SBATCH_NAME}.err

}

#
# Port Forwarding
#

function setup_port_forwarding() {

    echo
    echo "== Setting up port forwarding =="
    sleep 5
    if $ISOLATEDCOMPUTENODE
    then 
       echo "ssh -L $PORT:localhost:$PORT ${RESOURCE} ssh -L $PORT:localhost:$PORT -N $MACHINE &"
       ssh -L $PORT:localhost:$PORT ${RESOURCE} ssh -L $PORT:localhost:$PORT -N "$MACHINE" &
    else
       echo "ssh $DOMAINNAME -l $FORWARD_USERNAME -K -L  $PORT:$MACHINE:$PORT -N  &"
       ssh "$DOMAINNAME" -l $FORWARD_USERNAME -K -L  $PORT:$MACHINE:$PORT -N  &
    fi
}
"""
