#!/bin/bash

# Print out memory footprint of a command in 1 second interval.

if [ $# -ne 1 ]
then
	echo "Usage: $0 <command name>"
	exit 1
fi

COMM=$1
PID=`ps -eo pid,comm | grep $COMM | head -n 1 | awk '{print $1}'`

echo "vsz	rss	pid	cmd"
while true;
do
	PIDS=`./subprocs.py $PID`
	for P in $PIDS
	do
		ps -o vsz=,rss=,pid=,cmd= -f $P
	done
	sleep 1
done