# Fully Text-To-Speech Demo using Continuous Vocoder

[![Build Status](https://travis-ci.org/malradhi/merlin.svg?branch=master)](https://travis-ci.org/malradhi/merlin)



As a difference with other traditonal statistical parametric vocoders, continuous model focuses on extracting continuous parameters:
* Fondamental Frequency (F0)
* Maximum voice Freuqency (MVF)
* Mel-Generalized Cepstral (MGC) 




To run this demo, `cd egs/slt_arctic/s1` and follow the below steps:

Basically, ```run_full_data.sh``` script will:

## Setting up

The first step is to check continuous vocoder requirements in your system.
```sh
./01_chk_rqmts.sh
```

The second step is to run setup as it creates directories in ```./experiments``` and downloads the required training data files.

```sh
./02_setup.sh slt_arctic_full
```
OR
```sh
./02_setup.sh bdl_arctic_full
```

It also creates a global config file: `conf/global_settings.cfg`, where default settings are stored.
 
## Prepare config files

At this point, we have to prepare two config files to train DNN models
- Acoustic Model
- Duration Model

To prepare config files:
```sh
./03_prepare_conf_files.sh conf/global_settings.cfg
```

## Train duration model

To train duration model:
```sh
./04_train_duration_model.sh conf/duration_slt_arctic_full.conf
```

## Train acoustic model

To train acoustic model:
```sh
./05_train_acoustic_model.sh conf/acoustic_slt_arctic_full.conf
```
## Synthesize speech

To synthesize speech with continuous vocoder:
```sh
./06_run_merlin.sh conf/test_dur_synth_slt_arctic_full.conf conf/test_synth_slt_arctic_full.conf
```
The synthesised waveforms will be stored in: ```/<experiment_dir>/test_synthesis/wav```



# Test your TTS demo with continuous vocoder

## Requirements

You need to have installed:
* festival: ```bash tools/compile_other_speech_tools.sh```
* htk: ```bash tools/compile_htk.sh``

## If you want to test the trained version, ```tts_demo.sh``` script will

1. Create the txt directory in ```./experiments/slt_arctic_full/test_synthesis```.
2. ask you to enter a new sentenece.
3. Synthesise speech with continuous vocoder 





Contact Us
----------

Post your questions, suggestions, and discussions to [GitHub Issues](https://github.com/malradhi/merlin/issues).
"[Speech Technology and Smart Interactions Laboratory] (http://smartlab.tmit.bme.hu/index-en)"

Citation
--------

If you publish work based on Continuous+Merlin TTS, please cite: 

Al-Radhi M.S., Csapó T.G., Németh G. (2017) "[Deep Recurrent Neural Networks in Speech Synthesis Using a Continuous Vocoder] (https://link.springer.com/content/pdf/10.1007%2F978-3-319-66429-3_27.pdf)". In: Karpov A., Potapova R., Mporas I. (eds) Speech and Computer. SPECOM 2017. Lecture Notes in Computer Science, vol 10458. Springer, Cham, Hatfield, UK.



# Merlin: The Neural Network (NN) based Speech Synthesis System


Installation
------------

Merlin uses the following dependencies:

- numpy, scipy
- matplotlib
- bandmat
- theano
- tensorflow (optional, required if you use tensorflow models)
- sklearn, keras, h5py (optional, required if you use keras models)

To install Merlin, `cd` merlin and run the below steps:

- Install some basic tools in Merlin
```sh
bash tools/compile_tools.sh
```
- Install python dependencies
```sh
pip install -r requirements.txt
```


