#!/bin/bash

MS_START=1000
MS_END=2000
MS_STEP=1000

export MS_START
export MS_END
export MS_STEP

./moonsniff-test-series.sh
./moonsniff-process-series.sh
