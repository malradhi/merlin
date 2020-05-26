#!/bin/bash


#########################################
######## Continuous vocoder   ###########
#########################################

echo ""
echo "Step 1: Check for missing packages"
echo ""


# sox
command -v sox >/dev/null 2>&1 || { echo -e >&2 "\nSox is not found, but can be installed with:\n\nsudo apt-get install sox\n"; exit 1; }

# sptk
command -v sptk >/dev/null 2>&1 || { echo >&2 "\nSPTK is not found, but can be installed with:\n\nsudo apt-get install sptk\n"; exit 1; }

# octave
command -v octave >/dev/null 2>&1 || { echo -e >&2 "\nOctave is not found, but can be installed with:\n\nsudo apt-get install octave\n"; exit 1; }



echo "check done...!"
echo ""



