#!/bin/bash

MS_START=${MS_START:-500}
MS_END=${MS_END:-1000}
MS_STEP=${MS_STEP:-500}

MS_TIME=${MS_TIME:-5}

for ((SEND_RATE=MS_START; SEND_RATE<=MS_END; SEND_RATE=SEND_RATE+MS_STEP));
do
	echo "Starting test for rate $SEND_RATE mbit\\s for $MS_TIME seconds"
	echo ""
	./moonsniff-test.sh --rate $SEND_RATE --time $MS_TIME --file /persistent/measurement-rate-$SEND_RATE
done
