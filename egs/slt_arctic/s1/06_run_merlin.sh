#!/bin/bash -e

global_config_file=conf/global_settings.cfg
source $global_config_file

if test "$#" -ne 2; then
    echo "################################"
	echo ""
    echo "Usage: Merlin with continuous vocoder"
    echo ""
    echo "./06_run_merlin.sh <path_to_test_dur_conf_file> <path_to_test_synth_conf_file>"
    echo ""
    echo "Default path to test duration conf file: conf/test_dur_synth_${Voice}.conf"
    echo "Default path to test synthesis conf file: conf/test_synth_${Voice}.conf"
    echo "################################"
    exit 1
fi

test_dur_config_file=$1
test_synth_config_file=$2


### Step 6: synthesize speech ###
echo "Step 6:" 

echo "synthesizing durations..."
./scripts/submit.sh ${MerlinDir}/src/run_merlin.py $test_dur_config_file

echo "continuous synthesizing speech..."
./scripts/submit.sh ${MerlinDir}/src/run_merlin.py $test_synth_config_file

echo ""
echo "deleting intermediate synthesis files..."
./scripts/remove_intermediate_files.sh $global_config_file

echo ""
echo "synthesized audio files are in: experiments/${Voice}/test_synthesis/wav"

echo ""
echo "All successfull!! Your demo voice based on continuous vocoder is ready :)"
echo ""
