#!/bin/bash

##################################################################################
#																				 #
#       Continuous vocoder based Merlin toolkit	for Text-To-Speech (TTS)		 #
#       Works only with 16 kHz WAV files									     #
#																			     #
#       Author:																     #
#       Mohammed Salah Al-Radhi, malradhi@tmit.bme.hu							 #
#       Tamas Gabor CSAPO, csapot@tmit.bme.hu	                                 #
#													                             #													
##################################################################################


if test "$#" -ne 0; then
    echo "Usage: ./run_full_voice.sh"
    exit 1
fi


# step 1: check for missing packages
./01_chk_rqmts.sh


if [ $? -eq 0 ]; then


	### Step 2: setup directories and the training data files ###
	### To run on bdl full data --> ./02_setup.sh bdl_arctic_full
	./02_setup.sh slt_arctic_full

	### Step 3: prepare config files for acoustic, duration models and for synthesis ###
	./03_prepare_conf_files.sh conf/global_settings.cfg

	### Step 4: train duration model ###
	./04_train_duration_model.sh conf/duration_slt_arctic_full.conf

	### Step 5: train acoustic model ###
	./05_train_acoustic_model.sh conf/acoustic_slt_arctic_full.conf 

	### Step 6: synthesize speech ###
	./06_run_merlin.sh conf/test_dur_synth_slt_arctic_full.conf conf/test_synth_slt_arctic_full.conf 


else
    echo ""
fi


