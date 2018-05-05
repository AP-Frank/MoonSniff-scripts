#!/bin/bash

#fill in default values to avoid setting to many options
GENERATOR=user@some.server.com
GENERATOR_PATH=moonsniff/MoonGen/
GENERATOR_PORT="1 0"

SNIFFER=user@some.server.com
SNIFFER_PATH=moonsniff/MoonGen/
SNIFFER_PORT="1 0"
SNIFFER_OUTPUT=measurements
SNIFFER_LIVE=""

while :; do
	case $1 in
		-h|--help)
			echo "Some helpful information"
			exit
			;;
		-t|--time)
			RUN_TIME="$2"
			shift
			;;
		-r|--rate)
			SEND_RATE="$2"
			shift
			;;
		-s|--sniffports)
			SNIFFER_PORT="$2 $3"
			shift
			shift
			;;
		-g|--genports)
			GENERATOR_PORT="$2 $3"
			shift
			shift
			;;
		-f|--file)
			SNIFFER_OUTPUT="--output $2"
			shift
			;;
		-l|--live)
			SNIFFER_LIVE="--live"
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
SNIFFER_COMMAND="sleep 2 | ./${SNIFFER_PATH}build/MoonGen ${SNIFFER_PATH}examples/moonsniff/sniffer.lua ${SNIFFER_PORT} ${SNIFFER_LIVE} -r ${RUN_TIME} ${SNIFFER_OUTPUT}"
GENERATOR_COMMAND="./${GENERATOR_PATH}build/MoonGen ${GENERATOR_PATH}examples/moonsniff/traffic-gen.lua ${GENERATOR_PORT} -s ${SEND_RATE} -r $(( $RUN_TIME + 4 ))"

echo Executing the following command\(s\):$'\n\t' $SNIFFER_COMMAND$'\n\n' > logfiles/sniffer.log
echo Executing the following command\(s\):$'\n\t' $GENERATOR_COMMAND$'\n\n' > logfiles/generator.log

ssh ${GENERATOR} ${GENERATOR_COMMAND} >> logfiles/generator.log 2>&1 &
ssh ${SNIFFER} ${SNIFFER_COMMAND} >> logfiles/sniffer.log 2>&1 &
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
