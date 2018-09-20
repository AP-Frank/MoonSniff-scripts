#!/bin/bash

source configuration.sh

FILE_1=""
FILE_2=""
PROCESSOR_INPUT_1=""
PROCESSOR_INPUT_2=""

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
		-r|--rate)
			SEND_RATE="-$2"
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

mkdir -p logfiles

# build the commands
PROCESSOR_COMMAND="./${PROCESSOR_PATH}build/MoonGen ${PROCESSOR_PATH}examples/moonsniff/post-processing.lua ${PROCESSOR_INPUT_1} ${PROCESSOR_INPUT_2} ${PROCESSOR_OUTPUT} --nrbuckets ${PROCESSOR_BUCKET_SIZE}"

echo Executing the following command\(s\):$'\n\t' $PROCESSOR_COMMAND$'\n\n' > logfiles/processor${SEND_RATE}.log

printf "Starting processing of input .. "
ssh ${PROCESSOR} ${PROCESSOR_COMMAND} >> logfiles/processor${SEND_RATE}.log 2>&1
printf "Done\n"


if [ "$PROCESSOR_DELETE" = true ] ; then
	printf "Removing leftover files .. "
	ssh ${PROCESSOR} rm $FILE_1 $FILE_2 >> logfiles/processor${SEND_RATE}.log 2>&1
	printf "Done\n"
fi
