#!/bin/bash


###############################################################
#        Check requirements for continuous vocoder            #
###############################################################

echo ""
echo "Step 1: Check for missing packages"
echo ""


# sox
command -v sox >/dev/null 2>&1 || { echo -e >&2 "\nSox is not found, but can be installed with:\n\nsudo apt-get install sox\n"; exit 1; }

# sptk
command -v sptk >/dev/null 2>&1 || { echo >&2 "\nSPTK is not found, but can be installed with:\n\nsudo apt-get install sptk\n"; exit 1; }

# octave
command -v octave >/dev/null 2>&1 || { echo -e >&2 "\nOctave is not found, but can be installed with:\n\nsudo apt-get install octave\n"; exit 1; }



# festival
current_working_dir=$(pwd)
cd /usr/share/doc/festival/examples/
gunzip -f dumpfeats.gz
gunzip -f dumpfeats.sh.gz
chmod a+rx /usr/share/doc/festival/examples/dumpfeats
chmod a+rx /usr/share/doc/festival/examples/dumpfeats.sh
cd $current_working_dir



echo "check done...!"
echo ""



