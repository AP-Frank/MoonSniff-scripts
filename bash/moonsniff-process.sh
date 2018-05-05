#!/bin/bash

#fill in default values to avoid setting to many options

PROCESSOR=user@some.server.com
PROCESSOR_PATH=moonsniff/MoonGen/
FILE_1=""
FILE_2=""
PROCESSOR_INPUT_1=/persistent/measurements-pre.mscap
PROCESSOR_INPUT_2=/persistent/measurements-post.mscap
PROCESSOR_DELETE=false

while :; do
	case $1 in
		-h|--help)
			echo "Some helpful information"
			exit
			;;
		-f|--first-file)
			FILE_1="$2"
			PROCESSOR_INPUT_1="--input $2"
			shift
			;;
		-s|--second-file)
			FILE_2="$2"
			PROCESSOR_INPUT_2="--second-input $2"
			shift
			;;
		-o|--output)
			PROCESSOR_OUTPUT="--output $2"
			shift
			;;
		-d|--delete)
			PROCESSOR_DELETE=true
			;;
		-?*)
			printf 'WARN: Unknown option (abort): %s\n' "$1" >&2
			exit
			;;
		*)
			break
	esac
	shift
done

mkdir -p logfiles

# build the commands
PROCESSOR_COMMAND="./${PROCESSOR_PATH}build/MoonGen ${PROCESSOR_PATH}examples/moonsniff/post-processing.lua ${PROCESSOR_INPUT_1} ${PROCESSOR_INPUT_2} ${PROCESSOR_OUTPUT}"

echo Executing the following command\(s\):$'\n\t' $PROCESSOR_COMMAND$'\n\n' > logfiles/processor.log

printf "Starting processing of input .. "
ssh ${PROCESSOR} ${PROCESSOR_COMMAND} >> logfiles/processor.log 2>&1
printf "Done\n"


if [ "$PROCESSOR_DELETE" = true ] ; then
	printf "Removing leftover files .. "
	ssh ${PROCESSOR} rm $FILE_1 $FILE_2 >> logfiles/processor.log 2>&1 
	printf "Done\n"
fi
