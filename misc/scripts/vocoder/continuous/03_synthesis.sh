#!/bin/sh

	
#########################################
######## Continuous vocoder   ###########
#########################################


echo ""
echo "Step 3: Synthesis by Continuous vocoder"
echo ""	

current_working_dir=$(pwd)

lf0_dir=${current_working_dir}/example/analysis/lf0/
mvf_dir=${current_working_dir}/example/analysis/mvf/
mgc_dir=${current_working_dir}/example/analysis/mgc/

synthesis=${current_working_dir}/example/synthesis/
mkdir -p ${synthesis}		

python3 cont_speech_synthesis.py ${synthesis} ${lf0_dir} ${mvf_dir} ${mgc_dir}

cp -a ${current_working_dir}/example/wav/. ${current_working_dir}/example/synthesis/


echo ""
echo "deleting intermediate synthesis files..."
echo ""

rm ${synthesis}/*_float32.wav
rm ${synthesis}/*_pulsenoise.wav
rm ${synthesis}/*_0.wav


echo "synthesized audio files are in: ${current_working_dir}/example/synthesis"
echo ""
