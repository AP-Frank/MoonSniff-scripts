#!/bin/bash

source configuration.sh

for ((SEND_RATE=MS_START; SEND_RATE<=MS_END; SEND_RATE=SEND_RATE+MS_STEP));
do
	echo "Starting test for rate $SEND_RATE mbit\\s for $MS_TIME seconds"
	echo ""
	./moonsniff-test.sh --rate $SEND_RATE --file ${SNIFFER_OUT_FILE}-rate-$SEND_RATE
done
