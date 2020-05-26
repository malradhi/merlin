#!/usr/bin/env python


'''
Continuous vocoder based Merlin toolkit
Works only with 16 kHz WAV files


Author
- Tamas Gabor CSAPO, csapot@tmit.bme.hu
- Mohammed Salah Al-Radhi, malradhi@tmit.bme.hu

Nov 2016 - Jan 2017 - Oct 2018 - Jan 2020 ...

requirement: SPTK 3.8 or above in PATH folder


Reference
    [1] Mohammed Salah Al-Radhi, Tamás Gábor Csapó, Géza Németh, Time-domain envelope
        modulating the noise component of excitation in a continuous residual-based vocoder
        for statistical parametric speech synthesis, in Proceedings of the 18th Interspeech conference,
        pp. 434-438, Stockholm, Sweeden, 2017.
'''


import numpy as np
import scipy
from scipy.io import wavfile
import scipy.io.wavfile as io_wav
import pysptk
import os
import sys
from subprocess import call, run
import matplotlib.pyplot as plt
import ssp


####################### Global Variables ##########################################################


framePeriod = 80
loPitch=50
hiPitch=350

Fs = 16000

wav_path = sys.argv[1]
lf0_path = sys.argv[2] 
mvf_path = sys.argv[3] 
mgc_path = sys.argv[4]
 

octave = '/usr/bin/octave-cli'   

if not os.path.exists(lf0_path):
    os.mkdir(lf0_path)

if not os.path.exists(mvf_path):
    os.mkdir(mvf_path)
	
if not os.path.exists(mgc_path):
    os.mkdir(mgc_path)	
	
####################### Continuous Pitch Algorithm ################################################

def get_pitch(wav_path, basefilename):

    (Fs, x) = io_wav.read(wav_path + basefilename + '.wav')
        
    assert Fs == 16000
        
    pcm = ssp.PulseCodeModulation(Fs)
        

    frameSize = pcm.seconds_to_period(0.025, 'atleast') # 25ms Frame size
    pitchSize = pcm.seconds_to_period(0.1, 'atmost')   # 100ms Pitch size
    
    pf = ssp.Frame(x, size=pitchSize, period=framePeriod)
    pitch, ac= ssp.ACPitch(pf, pcm, loPitch, hiPitch)  # Initially pitch estimated

    # Pre-emphasis
    pre = ssp.parameter("Pre", None)
    if pre is not None:
        x = ssp.PoleFilter(x, pre) / 5
    
    # Frame Splitting
    f = ssp.Frame(x, size=frameSize, period=framePeriod)   

    # Windowing
    aw = ssp.nuttall(frameSize+1)        
    aw = np.delete(aw, -1)
    w = ssp.Window(f, aw)
    
    # Autocorrelation    
    ac = ssp.Autocorrelation(w)   

    if (len(ac) > len(pitch)):
        d = len(ac) - len(pitch)
        addon = np.ones(d) * pitch[-1]
        pitch = np.hstack((pitch, addon))
        
    # Save pitch as binary
    lf0 = np.log(pitch)
    lf0.astype('float32').tofile(lf0_path + basefilename + '.lf0')
  
    return pitch


###############################  get_MVF  #########################################################

def get_MVF(wav_path, basefilename):
    
    in_wav = wav_path + basefilename + '.wav'
    in_lf0i = lf0_path + basefilename + '.lf0'
    in_mvfi = mvf_path + basefilename + '.mvf'
    
    # Get Maximum Voiced Frequency
    command = octave + " --silent --eval \"MaximumVoicedFrequencyEstimation_nopp_run('" + \
        in_wav + "', '" + in_lf0i + "', '" + in_mvfi + "')\""
    #print('wav, lf0i -> mvfi, ' + in_wav)
    #print("command=", command)
    call(command, shell=True)
    
    # read in binary mvf file
    with open(in_mvfi, 'rb') as f:
        mvf = np.exp(np.fromfile(f, dtype=np.float32))
    
    return mvf


################################## Main program ############################################################################


# encode lf0 and mvf files
for wav_file in os.listdir(wav_path):
    if '.wav' in wav_file and 'synthesized' not in wav_file and 'source' not in wav_file and 'residual' not in wav_file:
        basefilename = wav_file[:-4]
        print('starting encoding of file: ' + basefilename)
        
        
        # calculate LF0 and MVF
        if not os.path.exists(lf0_path + basefilename + '.lf0'):
            get_pitch(wav_path, basefilename)
        if not os.path.exists(mvf_path + basefilename + '.mvf'):
            get_MVF(wav_path, basefilename)
            
        print(' ')
        


