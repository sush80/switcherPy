#!/bin/bash
SERVER=192.168.1.1

sleep 1

while true ; do
	# Only send two pings, sending output to /dev/null
	ping -c2 ${SERVER} > /dev/null
	
	if [ $? != 0 ]
	then
		echo "Network connection down! Attempting reconnection."	
		systemctl daemon-reload
		sleep 10
		systemctl restart dhcpcd
		sleep 60
	else
		sleep 10
	fi
done
