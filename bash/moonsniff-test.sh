#!/bin/bash

source configuration.sh

RUN_TIME=${MS_TIME:-20}

while :; do
	case $1 in
		-h|--help)
			echo "Some helpful information"
			exit
			;;
		-r|--rate)
			SEND_RATE="$2"
			shift
			;;
		-f|--file)
			SNIFFER_OUTPUT="--output $2"
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
SNIFFER_COMMAND="sleep 2 | ./${SNIFFER_PATH}build/MoonGen ${SNIFFER_PATH}examples/moonsniff/sniffer.lua ${SNIFFER_PORT} -t ${RUN_TIME} ${SNIFFER_OUTPUT} ${SNIFFER_FLAGS}"
GENERATOR_COMMAND="./${GENERATOR_PATH}build/MoonGen ${GENERATOR_PATH}examples/moonsniff/traffic-gen.lua ${GENERATOR_PORT} -r ${SEND_RATE} -t $(( $RUN_TIME + 4 ))"

echo Executing the following command\(s\):$'\n\t' $SNIFFER_COMMAND$'\n\n' > logfiles/sniffer-${SEND_RATE}.log
echo Executing the following command\(s\):$'\n\t' $GENERATOR_COMMAND$'\n\n' > logfiles/generator-${SEND_RATE}.log

ssh ${GENERATOR} ${GENERATOR_COMMAND} >> logfiles/generator-${SEND_RATE}.log 2>&1 &
ssh ${SNIFFER} ${SNIFFER_COMMAND} >> logfiles/sniffer-${SEND_RATE}.log 2>&1 &
(
# the used progressbar is based on https://github.com/fearside/ProgressBar/

# approximated total runtime, tests take a few seconds longer because of 
# bootstrapping DPDK etc.
duration=$(( $RUN_TIME + 6 ))

already_done() { for ((done=0; done<$elapsed; done++)); do printf "#"; done }
remaining() { for ((remain=$elapsed; remain<$duration; remain++)); do printf " "; done }
percentage() { printf "] %s%%" $(( (($elapsed)*100)/($duration)*100/100 )); }
clean_line() { printf "\r"; }

printf "Progress:\n"
for (( elapsed=1; elapsed<=$duration; elapsed++ )); do
	clean_line
	printf "["
	already_done; remaining; percentage
	sleep 1
done
printf "\n\nMeasurements should be finished shortly.\n"
printf "In case of live processing it might take longer.\n"
) &
wait

printf "Done\n\n"
