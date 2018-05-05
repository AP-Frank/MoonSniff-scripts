#!/bin/bash

MS_START=${MS_START:-500}
MS_END=${MS_END:-1000}
MS_STEP=${MS_STEP:-500}

for ((SEND_RATE=MS_START; SEND_RATE<=MS_END; SEND_RATE=SEND_RATE+MS_STEP));
do
	echo "Starting processing for rate ${SEND_RATE}."
	echo ""
	./moonsniff-process.sh --first-file /persistent/measurement-rate-${SEND_RATE}-pre.mscap --second-file /persistent/measurement-rate-${SEND_RATE}-post.mscap --output /persistent/hist-${SEND_RATE}
done
