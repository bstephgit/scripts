#!/bin/bash

INPUT_FILE=inputproxys.txt
OUTPUT_FILE=jdproxies.txt
TEMP_FILE=goodproxies_$RANDOM.txt
PARAM_POINTER=''

SCRIPT_PATH=$(dirname `which $0`)

if [ -z $SCRIPT_PATH ]; then
				echo cannot get script path for $0 ==> "$SCRIPT_PATH"
				exit
fi

while (( "$#" )); do
	key="$1"

	case $key in 
				-f)
					PARAM_POINTER=INPUT_FILE
					;;
				-o)
					PARAM_POINTER=OUTPUT_FILE
					;;
				*)
					if [ -n "$PARAM_POINTER" ]; then
						eval $PARAM_POINTER=$1
						PARAM_POINTER=""
					else
						echo unsuported argument "$key"
						exit
					fi
					;;
	esac
	shift
done

echo Input file: $INPUT_FILE
echo Output file: $OUTPUT_FILE
echo Temp file: $TEMP_FILE

PYTHON=`which python3`

if [ -z $PYTHON ]; then
	echo python3 path not found
	exit
fi

$PYTHON $SCRIPT_PATH/python/test_socks5_server.py -f $INPUT_FILE -o $TEMP_FILE

cat $TEMP_FILE | while read line ; do
	echo socks5://$line >> $OUTPUT_FILE
done

rm $TEMP_FILE
