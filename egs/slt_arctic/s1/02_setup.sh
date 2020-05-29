#!/bin/bash

if test "$#" -ne 1; then
    echo "################################"
	echo ""
    echo "Usage: Merlin with continuous vocoder"
    echo ""
	echo "Chose any of the below datasets" 
    echo "To run on full data:"
    echo "./02_setup.sh slt_arctic_full"
    echo "./02_setup.sh bdl_arctic_full"
    echo "################################"
    exit 1
fi

### Step 2: setup directories and the training data files ###
echo "Step 2:"

current_working_dir=$(pwd)
merlin_dir=$(dirname $(dirname $(dirname $current_working_dir)))
experiments_dir=${current_working_dir}/experiments

voice_name=$1
voice_dir=${experiments_dir}/${voice_name}

acoustic_dir=${voice_dir}/acoustic_model
duration_dir=${voice_dir}/duration_model
synthesis_dir=${voice_dir}/test_synthesis

mkdir -p ${experiments_dir}
mkdir -p ${voice_dir}
mkdir -p ${acoustic_dir}
mkdir -p ${duration_dir}

echo "downloading data....."


if [ "$voice_name" == "slt_arctic_full" ]
then
	if [[ ! -f ${voice_name}.zip ]]; then
		data_dir=slt_arctic_full
		python download_gdrive.py 12_9ta8sa5iHi649n1GEy2ZIwzOzfOGs7 ${voice_name}.zip
	else
		echo "the database already exists..."
	do_unzip=true
	fi
	
elif [ "$voice_name" == "bdl_arctic_full" ]
then

	if [[ ! -f ${voice_name}.zip ]]; then
		data_dir=bdl_arctic_full
		python download_gdrive.py 1rgaqRhnq7R5_HX1ONLQ_3iAicorQcJe8 ${voice_name}.zip
	else
		echo "the database already exists..."
	do_unzip=true
	fi
fi	

if [[ ! -d ${data_dir} ]] || [[ -n "$do_unzip" ]]; then
    echo "unzipping files......"
    rm -fr ${data_dir}
    rm -fr ${duration_dir}/data
    rm -fr ${acoustic_dir}/data
    unzip -q ${data_dir}.zip
    mv ${data_dir}/merlin_baseline_practice/duration_data/ ${duration_dir}/data
    mv ${data_dir}/merlin_baseline_practice/acoustic_data/ ${acoustic_dir}/data
    mv ${data_dir}/merlin_baseline_practice/test_data/ ${synthesis_dir}
fi

rm -f ${voice_name}.zip

echo "data is ready!"

global_config_file=conf/global_settings.cfg

### default settings ###
echo "MerlinDir=${merlin_dir}" >  $global_config_file
echo "WorkDir=${current_working_dir}" >>  $global_config_file
echo "Voice=${voice_name}" >> $global_config_file
echo "Labels=state_align" >> $global_config_file
echo "QuestionFile=questions-radio_dnn_416.hed" >> $global_config_file


echo "Vocoder=continuous" >> $global_config_file
echo "SamplingFreq=16000" >> $global_config_file


echo "FileIDList=file_id_list_full.scp" >> $global_config_file
echo "Train=1000" >> $global_config_file 
echo "Valid=66" >> $global_config_file 
echo "Test=66" >> $global_config_file 



echo "Merlin+continuous default voice settings configured in $global_config_file"
echo "setup done with continuous vocoder ...!"

