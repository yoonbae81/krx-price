#!/bin/bash
# Use environment variables or defaults
# Use fixed internal paths
DATE=${1:-`date +%Y-%m-%d`}
DIR="/app/src"
OUTPUT_DIR="/data"

echo "[INFO] Starting market data collection for $DATE"

######################
# Symbols
######################
SYMBOLS=$(mktemp /tmp/symbols.XXXX)
$DIR/symbol.py > $SYMBOLS
echo "[INFO] Found $(wc -l < $SYMBOLS) symbols"

######################
# Day
######################
TEMP=$(mktemp /tmp/day.XXXX)
# New async version handles parallelism internally
$DIR/day.py -d $DATE -f $SYMBOLS -c 20 > $TEMP
mkdir -p $OUTPUT_DIR/day
sort $TEMP > $OUTPUT_DIR/day/$DATE.txt
echo "[INFO] Day data collected: $(wc -l < $OUTPUT_DIR/day/$DATE.txt) lines"

######################
# Minute
######################
TEMP=$(mktemp /tmp/minute.XXXX)
# New async version handles parallelism internally
$DIR/minute.py -d $DATE -f $SYMBOLS -c 20 > $TEMP
mkdir -p $OUTPUT_DIR/minute
sort -k4 $TEMP > $OUTPUT_DIR/minute/$DATE.txt
echo "[INFO] Minute data collected: $(wc -l < $OUTPUT_DIR/minute/$DATE.txt) lines"

echo "[INFO] Market data collection finished for $DATE"
rm -f $SYMBOLS $TEMP
