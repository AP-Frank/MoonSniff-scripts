#!/bin/bash

#fill in default values to avoid setting to many options

PROCESSOR=user@some.server.com
PROCESSOR_PATH=moonsniff/MoonGen/
PROCESSOR_INPUT_1=/persistent/measurements-pre.mscap
PROCESSOR_INPUT_2=/persistent/measurements-post.mscap

while :; do
	case $1 in
		-h|--help)
			echo "Some helpful information"
			exit
			;;
		-f|--first-file)
			PROCESSOR_INPUT_1="--input $2"
			shift
			;;
		-s|--second-file)
			PROCESSOR_INPUT_2="--second-input $2"
			shift
			;;
		-o|--output)
			PROCESSOR_OUTPUT="--output $2"
			shift
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

mkdir logfiles

# build the commands
PROCESSOR_COMMAND="./${PROCESSOR_PATH}build/MoonGen ${PROCESSOR_PATH}examples/moonsniff/post-processing.lua ${PROCESSOR_INPUT_1} ${PROCESSOR_INPUT_2} ${PROCESSOR_OUTPUT}"

echo Executing the following command\(s\):$'\n\t' $PROCESSOR_COMMAND$'\n\n' > logfiles/processor.log

ssh ${PROCESSOR} ${PROCESSOR_COMMAND} >> logfiles/processor.log 2>&1
