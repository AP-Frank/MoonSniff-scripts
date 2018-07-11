#!/bin/bash

source configuration.sh

mkdir -p logfiles
cp configuration.sh logfiles/config

for ((SEND_RATE=MS_START; SEND_RATE<=MS_END; SEND_RATE=SEND_RATE+MS_STEP));
do
	echo "Starting measurement for rate $SEND_RATE mbit\\s for $MS_TIME seconds .. "
	echo ""
	./moonsniff-test.sh --rate $SEND_RATE --file ${SNIFFER_OUT_FILE}-rate-$SEND_RATE

	# start processing

	FILE_PRE="${SNIFFER_OUT_FILE}-rate-${SEND_RATE}-pre.${SNIFFER_MODE}"
	FILE_POST="${SNIFFER_OUT_FILE}-rate-${SEND_RATE}-post.${SNIFFER_MODE}"

	./moonsniff-process.sh --first-file $FILE_PRE --second-file $FILE_POST --output ${PROCESSOR_OUT_FILE}-${SEND_RATE}
done
