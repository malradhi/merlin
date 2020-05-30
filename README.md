# SLT Arctic TTS Demo using MagPhase Vocoder

## Continuous Vocoder in DNN-TTS system

It is a Text-To-Speech demo using the continuous vocoder.


As a difference with other traditonal statistical, it focuses on extracting continuous parameters:
* Fondamental Frequency (F0)
* Maximum voice Freuqency (MVF)
* Mel-Generalized Cepstral (MGC) 

Basically, ```run_full_data.sh``` script will:

1. Download the input data for you.
2. Create the experiment directory in ```./experiments```.
3. Perform acoustic feature extraction with continuous vocoder.
4. Build and train duration and acoustic models using Merlin.
5. Synthesise waveforms using predicted durations. The synthesised waveforms will be stored in: ```/<experiment_dir>/test_synthesis/wav```


## Build your demo with continuous vocoder


If you want to test the trained version, ```tts_demo.sh``` script will

1. Create the txt directory in ```./experiments/slt_arctic_full/test_synthesis```.
2. ask you to enter a new sentenece.
3. Synthesise speech with continuous vocoder 



## Requirements

You need to have installed:
* festival: ```bash tools/compile_other_speech_tools.sh```
* htk: ```bash tools/compile_htk.sh``



##
##
##
#
#
#
#
#



# TTS Demo using Continuous Vocoder


To run this demo, `cd egs/slt_arctic/s1` and follow the below steps:

## Setting up

The first step is to run setup as it creates directories and downloads the required training data files.

To see the list of available voices, run:
```sh
./01_setup.sh
```
The next steps demonstrate on how to setup slt arctic voice. 

- To run on short data(about 50 utterances for training)
```sh
./01_setup.sh slt_arctic_demo
```
- To run on full data(about 1000 sentences for training)
```sh
./01_setup.sh slt_arctic_full
```

It also creates a global config file: `conf/global_settings.cfg`, where default settings are stored.
 
## Prepare config files

At this point, we have to prepare two config files to train DNN models
- Acoustic Model
- Duration Model

To prepare config files:
```sh
./02_prepare_conf_files.sh conf/global_settings.cfg
```
Four config files will be generated: two for training, and two for testing. 

## Train duration model

To train duration model:
```sh
./03_train_duration_model.sh <path_to_duration_conf_file>
```

## Train acoustic model

To train acoustic model:
```sh
./04_train_acoustic_model.sh <path_to_acoustic_conf_file>
```
## Synthesize speech

To synthesize speech:
```sh
./05_run_merlin.sh <path_to_test_dur_conf_file> <path_to_test_synth_conf_file>
```











[![Build Status](https://travis-ci.org/CSTR-Edinburgh/merlin.svg?branch=master)](https://travis-ci.org/CSTR-Edinburgh/merlin)

## Merlin: The Neural Network (NN) based Speech Synthesis System

This repository contains the Neural Network (NN) based Speech Synthesis System  
developed at the Centre for Speech Technology Research (CSTR), University of 
Edinburgh. 

Merlin is a toolkit for building Deep Neural Network models for statistical parametric speech synthesis. 
It must be used in combination with a front-end text processor (e.g., Festival) and a vocoder (e.g., STRAIGHT or WORLD).

The system is written in Python and relies on the Theano numerical computation library.

Merlin comes with recipes (in the spirit of the [Kaldi](https://github.com/kaldi-asr/kaldi) automatic speech recognition toolkit) to show you how to build state-of-the art systems.

Merlin is free software, distributed under an Apache License Version 2.0, allowing unrestricted commercial and non-commercial use alike.

Read the documentation at [cstr-edinburgh.github.io/merlin](https://cstr-edinburgh.github.io/merlin/).

Merlin is compatible with: __Python 2.7-3.6__.

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

For detailed instructions, to build the toolkit: see [INSTALL](https://github.com/CSTR-Edinburgh/merlin/blob/master/INSTALL.md) and [CSTR blog post](https://cstr-edinburgh.github.io/install-merlin/).  
These instructions are valid for UNIX systems including various flavors of Linux;


Getting started with Merlin
---------------------------

To run the example system builds, see `egs/README.txt`

As a first demo, please follow the scripts in `egs/slt_arctic`

Now, you can also follow Josh Meyer's [blog post](http://jrmeyer.github.io/tts/2017/02/14/Installing-Merlin.html) for detailed instructions <br/> on how to install Merlin and build SLT demo voice.

For a more in-depth tutorial about building voices with Merlin, you can check out:

- [Deep Learning for Text-to-Speech Synthesis, using the Merlin toolkit (Interspeech 2017 tutorial)](http://www.speech.zone/courses/one-off/merlin-interspeech2017)
- [Arctic voices](https://cstr-edinburgh.github.io/merlin/getting-started/slt-arctic-voice)
- [Build your own voice](https://cstr-edinburgh.github.io/merlin/getting-started/build-own-voice)


Synthetic speech samples
------------------------

Listen to [synthetic speech samples](https://cstr-edinburgh.github.io/merlin/demo.html) from our SLT arctic voice.

Development pattern for contributors
------------------------------------

1. [Create a personal fork](https://help.github.com/articles/fork-a-repo/)
of the [main Merlin repository](https://github.com/CSTR-Edinburgh/merlin) in GitHub.
2. Make your changes in a named branch different from `master`, e.g. you create
a branch `my-new-feature`.
3. [Generate a pull request](https://help.github.com/articles/creating-a-pull-request/)
through the Web interface of GitHub.

Contact Us
----------

Post your questions, suggestions, and discussions to [GitHub Issues](https://github.com/CSTR-Edinburgh/merlin/issues).

Citation
--------

If you publish work based on Merlin, please cite: 

Zhizheng Wu, Oliver Watts, Simon King, "[Merlin: An Open Source Neural Network Speech Synthesis System](https://isca-speech.org/archive/SSW_2016/pdfs/ssw9_PS2-13_Wu.pdf)" in Proc. 9th ISCA Speech Synthesis Workshop (SSW9), September 2016, Sunnyvale, CA, USA.

