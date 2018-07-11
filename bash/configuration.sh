#!/bin/bash

# this configuration file is sourced by all test-scripts
# vars which are not needed by the executed test need not be filled out
#
# setting start to end allows to execute a single rate test

# configuration for a whole test series
MS_START=500	# send-rate to start from [MBit/s]
MS_END=2000	# send-rate to end at [MBit/s]
MS_STEP=250	# value by which to increase the send-rate [MBit/s]
MS_TIME=20	# duration of the sending/capturing operation [sec]

# configuration for the traffic generator
GENERATOR=user@some.server.com		# ssh target for the traffic generator
GENERATOR_PATH=moonsniff/MoonGen/	# path to MoonGen source
GENERATOR_PORT="1 0"			# port [out]; port [in]

# configuration for the sniffer
SNIFFER=user@some.server.com			# ssh target for the sniffer
SNIFFER_PATH=moonsniff/MoonGen/			# path to MoonGen source
SNIFFER_PORT="1 0"				# port [in] pre; port [in] post
SNIFFER_OUT_FILE=/persistent/measurement	# path/filename to store output
SNIFFER_MODE="pcap"				# operation mode; pcap or mscap

# configurtion for the post-processor
PROCESSOR=user@some.server.com			# ssh target for the processor
PROCESSOR_PATH=moonsniff/MoonGen/		# path to MoonGen source
PROCESSOR_IN_FILE=/persistent/measurement	# path/filename for inputs
PROCESSOR_OUT_FILE=/persistent/hist		# path/filename for outputs
PROCESSOR_DELETE=false				# delete capture files (Big)
PROCESSOR_BUCKET_SIZE=1				# size of buckets [nsec]


###########################
# Do not touch below here #####################################################
###########################

if [ ${SNIFFER_MODE} = "mscap" ]; then
	SNIFFER_FLAGS=""
fi
if [ ${SNIFFER_MODE} = "pcap" ]; then
	SNIFFER_FLAGS="--capture"
fi
