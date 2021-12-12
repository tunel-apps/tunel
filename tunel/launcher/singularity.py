__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from tunel.logger import logger
import tunel.utils as utils
import tunel.ssh
import os

from tunel.launcher.base import Launcher


class Slurm(Launcher):
    """
    A slurm launcher interacts with slurm
    """

    def __init__(self, server, **kwargs):
        super().__init__(server, **kwargs)
        self._inventory = {}

    @property
    def modules_file(self):
        return os.path.join(self.assets_dir, "modules.txt")

    @property
    def nodes_file(self):
        return os.path.join(self.assets_dir, "sinfo.txt")

    def update_inventory(self):
        self._update_inventory_modules()
        self._update_inventory_nodes()

    def _update_inventory_nodes(self):
        """
        Try to derive attributes for nodes
        """
        if not os.path.exists(self.nodes_file):
            res = self.ssh.execute("scontrol show config")
            tunel.utils.write_file(self.nodes_file, res["message"])
        if os.path.exists(self.nodes_file) and "nodes" not in self._inventory:
            self._inventory["nodes"] = tunel.utils.read_config_file(self.nodes_file)

    def _update_inventory_modules(self):
        """
        Try to derive list of installed modules on cluster.
        This has been tested for LMOD
        """
        # if we don't have modules, write there
        if not os.path.exists(self.modules_file):
            res = self.scp_and_run("list_modules.sh")
            if res["return_code"] == 0:
                res = [x for x in res["message"].split("\n") if "RESULT:" in x]

                # This is the output file with list of modules
                if res:
                    res = res[0].split(":")[-1]

                    # scp get is copying FROM the server to assets here
                    self.scp_get(res, self.modules_file)

        # When we get here, only will exist if command was successful
        if os.path.exists(self.modules_file) and "modules" not in self._inventory:
            self._inventory["modules"] = tunel.utils.read_lines(self.modules_file)

    def run(self, *args, **kwargs):
        """
        Run a command for slurm, typically sbatch (and eventually with supporting args)
        """
        if not self._inventory:
            self.update_inventory()

        # If no command, get interactive node
        cmd = args[0]
        if not cmd:
            logger.info("No command supplied, will init interactive session!")
            self.ssh.shell("srun --pty bash", interactive=True)

        # TODO develop workflow for script
        else:
            res = self.ssh.execute("sbatch %s" % " ".join(cmd))
            self.ssh.print_output(res)


class Singularity(Launcher):
    def run(self, *args, **kwargs):
        """
        Run handles some command to singularity (e.g., run or exec)
        """
        command = "%s %s singularity %s" % (self.path, self.environ, " ".join(args[0]))

        # If the user wants a shell, give to them!
        if "shell" in args[0]:
            self.ssh.shell(command, interactive=True)
        else:
            res = self.ssh.execute(command)
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
