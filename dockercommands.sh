#!/bin/bash
######################### 
# Author: gw700
# Date: 15.06.2023
#########################

COMMANDS=("$1" "$2" "$3")

if [ "$1" = "rmi" ]
	then
		docker $1 $2 

elif [ "$1" = "pull" ]
	then
		docker $1 $2

elif [ "$1" = "push" ]
	then
		docker $1 $2

elif [ "$1" = "tag" ]
	then
		docker $1 $2 $3

fi

