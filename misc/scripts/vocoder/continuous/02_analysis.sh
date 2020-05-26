#!/bin/bash


#########################################
######## Continuous vocoder   ###########
#########################################

echo ""
echo "Step 2: Analysis by Continuous vocoder"
echo ""


# tools directory

current_working_dir=$(pwd)

wav_dir=${current_working_dir}/example/wav/

lf0_dir=${current_working_dir}/example/analysis/lf0/
mvf_dir=${current_working_dir}/example/analysis/mvf/
sp_dir=${current_working_dir}/example/analysis/sp/
mgc_dir=${current_working_dir}/example/analysis/mgc/


mkdir -p ${lf0_dir}
mkdir -p ${mvf_dir}
mkdir -p ${sp_dir}
mkdir -p ${mgc_dir}

# sampling frequency
fs=16000


# these numbers are valid only for fs=16 kHz
nFFTHalf=1024 
alpha=0.58 

#bap order depends on sampling freq.
mcsize=59


echo "extract continuous parameters: lf0, MVF, MGC"
echo  "take only a few seconds per wave file..."
echo ""


python3 cont_features_extraction.py ${wav_dir} ${lf0_dir} ${mvf_dir} ${mgc_dir}


for file in ${wav_dir}/*.wav
do
    filename="${file##*/}"
    file_id="${filename%.*}"
   
    
	### extract log spectrum (sp) ### 
	$current_working_dir/spec_env ${wav_dir}/$file_id.wav 0 ${sp_dir}/$file_id.sp 0
    
	### convert log spectrum (sp) to mel-generalized cepstrum (mgc) 
	sptk x2x +df ${sp_dir}/$file_id.sp | sptk sopr -R -m 32768.0 | sptk mcep -a $alpha -m $mcsize -l $nFFTHalf -e 1.0E-8 -j 0 -f 0.0 -q 3 > ${mgc_dir}/$file_id.mgcep
	
done

# echo "deleting intermediate analysis files..."
rm -rf $sp_dir 
rm -rf 0


echo ""
echo "the analysis part is done! ... parameters are in: ${current_working_dir}/example/analysis"
echo ""




