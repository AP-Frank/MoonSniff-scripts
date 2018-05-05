#!/bin/bash

MS_START=${MS_START:-500}
MS_END=${MS_END:-9000}
MS_STEP=${MS_STEP:-500}

MS_TIME=${MS_TIME:-20}

for ((SEND_RATE=MS_START; SEND_RATE<=MS_END; SEND_RATE=SEND_RATE+MS_STEP));
do
	echo "Starting measurement for rate $SEND_RATE mbit\\s for $MS_TIME seconds .. "
	echo ""
	./moonsniff-test.sh --rate $SEND_RATE --time $MS_TIME --file /persistent/measurement-rate-$SEND_RATE

	# start processing

	FILE_PRE="/persistent/measurement-rate-${SEND_RATE}-pre.mscap" 
	FILE_POST="/persistent/measurement-rate-${SEND_RATE}-post.mscap" 

	./moonsniff-process.sh --delete --first-file $FILE_PRE --second-file $FILE_POST --output /persistent/hist-${SEND_RATE}
done
