#!/bin/bash 
# job.sh: a short discovery job 
# This is part of the OSG tutorial-quickstart
printf "Start time: "; /bin/date 
printf "Job is running on node: "; /bin/hostname 
printf "Job running as user: "; /usr/bin/id 
printf "Job is running in directory: "; /bin/pwd 
echo
echo "Working hard..."
sleep 30
echo "Science complete!"
