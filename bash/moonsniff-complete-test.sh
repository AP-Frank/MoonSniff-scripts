#!/bin/bash

mkdir -p logfiles
cp configuration.sh logfiles/config

./moonsniff-test-series.sh
./moonsniff-process-series.sh
