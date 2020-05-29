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



import librosa
import matplotlib.pyplot as plt
import numpy as np
import numpy.linalg as linalg
import os
from os.path import splitext
import pysptk
from pysptk.synthesis import MGLSADF, Synthesizer
import scipy
from scipy.fftpack import fft, ifft
from scipy.io import wavfile
import scipy.io.wavfile as io_wav
from scipy.signal import hilbert, chirp
from shutil import move
import sys
import struct
from subprocess import call, run
import ssp


####################### Global Variables ##########################################################

framePeriod = 80
loPitch=50
hiPitch=350

Fs = 16000


gen_path = sys.argv[1]
octave   = '/usr/bin/octave-cli' 

frlen = 1024 # length of speech frames - should be order of 2, because of FFT
frshft = round(0.005 * Fs)   # 5ms Frame shift
order = 59
alpha = 0.58
stage = 0
gamma = 0
lpf_order = 10
hpf_order = 10

codebook_filename = ('resid_cdbk_awb_0080_pca.bin') # male
#codebook_filename = ('resid_cdbk_slt_0080_pca.bin') # female

noise_scaling = 0.08


#envelopes = ['Amplitude', 'Hilbert', 'Triangular', 'True']
envelopes = ['Hilbert']


#################################  filtering functions  ####################################################


def cheby1_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    # rp: The maximum ripple allowed below unity gain in the passband. Specified in decibels, as a positive number.
    b, a = scipy.signal.cheby1(order, 0.1, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data_l, cutoff, fs, order=5):
    b, a = cheby1_lowpass(cutoff, fs, order=order)
    y = scipy.signal.lfilter(b, a, data_l)
    return y

def cheby1_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    # rp: The maximum ripple allowed below unity gain in the passband. Specified in decibels, as a positive number.
    c, d = scipy.signal.cheby1(order, 0.1, normal_cutoff, btype='high', analog=False)
    return c, d

def highpass_filter(data_h, cutoff, fs, order=5):
    c, d = cheby1_highpass(cutoff, fs, order=order)
    z = scipy.signal.lfilter(c, d, data_h)
    return z


####################### Continuous Pitch Algorithm ################################################

def get_pitch(gen_path, basefilename):

    (Fs, x) = io_wav.read(gen_path + basefilename + '.wav')
        
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
    lf0.astype('float32').tofile(gen_path + basefilename + '.lf0')
  
    return pitch


###############################  get_MVF  #########################################################

def get_MVF(gen_path, basefilename):
    
    in_wav = gen_path + basefilename + '.wav'
    in_lf0i = gen_path + basefilename + '.lf0'
    in_mvfi = gen_path + basefilename + '.mvf'
    
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


##################################  Get Residual Signal ###########################################

# get residual signal with inverse filtering
# inverse filtering is done with outer SPTK tools
# in order for this to run, you will need SPTK binaries installed

def mgc_get_residual(basefilename):
   
    # read Fs
    (x, Fs) = wavread(basefilename + '.wav')    
    
    # output vector length = number of frames
    nframes = int(np.ceil(len(x) / frshft))
    
    in_wav = basefilename + '.wav'
    in_raw = basefilename + '.raw'
    in_mgcep = basefilename + '.mgc'
    in_resid = basefilename + '.resid.wav'
    
    # wav -> raw
    command = 'sox -c 1 -e signed-integer -b 16 -t wav ' + in_wav + \
        ' -c 1 -e signed-integer -b 16 -t raw -r ' + str(Fs) + ' ' + in_raw
    print('wav -> raw, ' + in_wav)
    call(command, shell=True)
    
    # raw -> mgcep
    command = 'sptk x2x +sf ' + in_raw + ' | ' + \
         'frame -l ' + str(frlen) + ' -p ' + str(frshft) + ' | ' + \
         'window -l ' + str(frlen) + ' -L 512 -w 1 -n 1 | ' + \
         'mgcep -a ' + str(alpha) + ' -c 3 -m ' + str(order) + ' -l 512 > ' + in_mgcep
    print('raw -> mgcep, ' + in_wav)
    call(command, shell=True)
    
    # wav, mgcep -> residual
    command = 'sptk x2x +sf ' + in_raw + ' | ' + \
        'mglsadf -k -v -a ' + str(alpha) + ' -c 3 -m ' + str(order) + ' -p ' + \
        str(frshft) + ' ' + in_mgcep + ' | ' + \
        'sptk x2x +fs | sox -c 1 -e signed-integer -b 16 -t raw -r ' + str(Fs) + ' - ' + \
        '-c 1 -e signed-integer -b 16 -t wav -r ' + str(Fs) + ' ' + in_resid
    # print(command)
    print('raw, mgcep -> resid.wav, ' + in_wav)
    call(command, shell=True)



    ################# read wave ######################
    for wav_file in os.listdir(gen_path):
        if '.wav' in wav_file:
            print('starting file: ' + wav_file)
            (x_residual, Fs_) = wavread(gen_path + wav_file)
    return x_residual



##################################  Read Residual Codebook ########################################

def read_residual_codebook(codebook_filename):
    file_in = open(codebook_filename, 'rb')
    f = file_in.read(4) # 4 byte int
    cdbk_size, = struct.unpack('i', f)
    f = file_in.read(4) # 4 byte int
    resid_pca_length, = struct.unpack('i', f)
    resid_pca = np.zeros((cdbk_size, resid_pca_length))
    for i in range(cdbk_size):
        if i > 0:
            f = file_in.read(4) # 4 byte int
            resid_pca_length, = struct.unpack('i', f)
        f = file_in.read(8 * resid_pca_length) # 8 byte double * resid_pca_length
        resid_pca_current = struct.unpack('<%dd' % resid_pca_length, f)
        resid_pca[i] = resid_pca_current
    
    return resid_pca

    
###################### Synthesis using Continuous Pitch + MVF + MGC + Residual ####################

def mgc_decoder_residual_without_envelope(pitch, mvf, mgc_coeff, resid_codebook_pca, basefilename):
    
    # create voiced source excitation using SPTK
    source_voiced = pysptk.excite(Fs / pitch, frshft)
    
    # create unvoiced source excitation using SPTK
    pitch_unvoiced = np.zeros(len(pitch))
    source_unvoiced = pysptk.excite(pitch_unvoiced, frshft)
    
    source = np.zeros(source_voiced.shape)
    
    # generate excitation frame by frame pitch synchronously
    for i in range(len(source)):
        if source_voiced[i] > 2: # location of impulse in original impulse excitation
            mvf_index = int(i / frshft)
            mvf_curr = mvf[mvf_index]
            
            if mvf_curr > 7500:
                mvf_curr = 7500
            
            # voiced component from binary codebook
            voiced_frame_lpf = resid_codebook_pca[int((Fs / 2 - 0.95 * mvf_curr) / 100)]
            
            # unvoiced component by highpass filtering white noise
            if i + len(voiced_frame_lpf) < len(source_unvoiced):
                unvoiced_frame = source_unvoiced[i : i + len(voiced_frame_lpf)].copy()
            else:
                unvoiced_frame = source_unvoiced[i - len(voiced_frame_lpf) : i].copy()
            
            unvoiced_frame_hpf = highpass_filter(unvoiced_frame, mvf_curr * 1.05, Fs, hpf_order)
            unvoiced_frame_hpf *= np.hanning(len(unvoiced_frame_hpf))
            
            # put voiced and unvoiced component to pitch synchronous location
            j_start = np.max((round(len(voiced_frame_lpf) / 2) - i, 0))
            j_end   = np.min((len(voiced_frame_lpf), len(source) - (i - round(len(voiced_frame_lpf) / 2))))
            for j in range(j_start, j_end):
                source[i - round(len(voiced_frame_lpf) / 2) + j] += voiced_frame_lpf[j]
                source[i - round(len(voiced_frame_lpf) / 2) + j] += unvoiced_frame_hpf[j] * noise_scaling
    
    # scale for SPTK
    scaled_source = np.float32(source / np.max(np.abs(source)) )
    io_wav.write(gen_path + basefilename + '_source_float32.wav', Fs, scaled_source)
    
    command = 'sox ' + gen_path + basefilename + '_source_float32.wav' + ' -t raw -r ' + str(Fs) + ' - ' + ' | ' + \
              'mglsadf -P 5 -m ' + str(order) + ' -p ' + str(frshft) + \
              ' -a ' + str(alpha) + ' -c ' + str(stage) + ' ' + gen_path + basefilename + '.mgc' + ' | ' + \
              'sptk x2x +fs -o | sox -c 1 -b 16 -e signed-integer -t raw -r ' + str(Fs) + ' - -t wav -r ' + str(Fs) + ' ' + gen_path + basefilename + '_synthesized_without_envelope_0.wav'
    ###print(command)
    run(command, shell=True)
    
    command = "sox -G " + gen_path + basefilename + '_synthesized_without_envelope_0.wav' + ' ' + \
        gen_path + basefilename + '_synthesized_without_envelope.wav'
    ###print(command)
    run(command, shell=True)
   
    return [0]


####################################################################################################################


def mgc_decoder_pulsenoise(pitch, mvf, mgc_coeff, resid_codebook_pca, basefilename):
    
    #print(len(pitch), len(mvf))
    
    T0 = np.zeros(np.min([len(pitch), len(mvf)]))
    mvf_mean = np.mean(mvf)
    # print(mvf_mean)
    
    for i in range(len(T0)):
        if mvf[i] < 0.4 * mvf_mean:
            T0[i] = 0
        elif pitch[i] > 0:
            T0[i] = Fs / pitch[i]
    
    # create source excitation using SPTK
    source = pysptk.excite(T0, frshft)
    
    # scale for SPTK
    scaled_source = np.float32(source / np.max(np.abs(source)) )
    io_wav.write(gen_path + basefilename + '_source_pulsenoise_float32.wav', Fs, scaled_source)
    
    command = 'sox ' + gen_path + basefilename + '_source_pulsenoise_float32.wav' + ' -t raw -r ' + str(Fs) + ' - ' + ' | ' + \
              'mglsadf -P 5 -m ' + str(order) + ' -p ' + str(frshft) + \
              ' -a ' + str(alpha) + ' -c ' + str(stage) + ' ' + gen_path + basefilename + '.mgc' + ' | ' + \
              'sptk x2x +fs -o | sox -c 1 -b 16 -e signed-integer -t raw -r ' + str(Fs) + ' - -t wav -r ' + str(Fs) + ' ' + gen_path + basefilename + '_synthesized_pulsenoise_0.wav'
    ###print(command)
    run(command, shell=True)
    
    command = "sox -G " + gen_path + basefilename + '_synthesized_pulsenoise_0.wav' + ' ' + \
        gen_path + basefilename + '_synthesized_pulsenoise.wav'
    ###print(command)
    run(command, shell=True)
    
    return [0]



####################################################################################################################


def mgc_filter_residual(pitch, mvf, mgc_coeff, resid_codebook_pca, basefilename):
    
    in_wav = gen_path + basefilename + '.wav'
    in_raw = gen_path + basefilename + '.raw'
    in_mgcep = gen_path + basefilename + '.mgc'
    in_resid = gen_path + basefilename + '_residual_original.wav'
    out_resid = gen_path + basefilename + '_residual_filtered.wav'
    
    # wav -> raw
    command = 'sox -c 1 -e signed-integer -b 16 -t wav ' + in_wav + \
        ' -c 1 -e signed-integer -b 16 -t raw -r ' + str(Fs) + ' ' + in_raw
    print('wav -> raw, ' + in_wav)
    call(command, shell=True)
    
    # raw, mgcep -> residual
    command = 'sptk x2x +sf ' + in_raw + ' | ' + \
        'mglsadf -k -v -a ' + str(alpha) + ' -c 3 -m ' + str(order) + ' -p ' + \
        str(frshft) + ' ' + in_mgcep + ' | ' + \
        'sptk x2x +fs | sox -c 1 -e signed-integer -b 16 -t raw -r ' + str(Fs) + ' - ' + \
        '-c 1 -e signed-integer -b 16 -t wav -r ' + str(Fs) + ' ' + in_resid
    # print(command)
    print('raw, mgcep -> resid.wav, ' + in_wav)
    call(command, shell=True)
    
    (Fs_, x_residual) = io_wav.read(in_resid)
    
    plt.plot(x_residual[0:Fs], 'r')
    plt.show()
    
    # create voiced source excitation using SPTK
    source_voiced = pysptk.excite(Fs / pitch, frshft)
    
    source_upper = np.zeros(source_voiced.shape)
    source_lower = np.zeros(source_voiced.shape)
    
    # generate excitation frame by frame pitch synchronously
    for i in range(len(source_upper)):
        if source_voiced[i] > 2: # location of impulse in original impulse excitation
            mvf_index = int(i / frshft)
            mvf_curr = mvf[mvf_index]
            T0_curr = int(Fs / pitch[mvf_index])
            
            if i > T0_curr and i + 2 * T0_curr < len(source_upper):
                residual_frame = x_residual[i - T0_curr : i + T0_curr]
                residual_frame_upper = highpass_filter(residual_frame, mvf_curr * 1.05, Fs, hpf_order)
                residual_frame_upper *= np.hanning(len(residual_frame_upper))
                source_upper[i - T0_curr : i + T0_curr] += residual_frame_upper
                
                residual_frame_lower = lowpass_filter(residual_frame, mvf_curr * 0.95, Fs, lpf_order)
                residual_frame_lower *= np.hanning(len(residual_frame_lower))
                source_lower[i - T0_curr : i + T0_curr] += residual_frame_lower
    
    # '''
    # upper frequency band
    scaled_source = np.float32(source_upper / np.max(np.abs(source_upper)) )
    io_wav.write(gen_path + basefilename + '_residual_upper_float32.wav', Fs, scaled_source)
    
    command = 'sox ' + gen_path + basefilename + '_residual_upper_float32.wav' + ' -t raw -r ' + str(Fs) + ' - ' + ' | ' + \
              'mglsadf -P 5 -m ' + str(order) + ' -p ' + str(frshft) + \
              ' -a ' + str(alpha) + ' -c ' + str(stage) + ' ' + gen_path + basefilename + '.mgc' + ' | ' + \
              'sptk x2x +fs -o | sox -c 1 -b 16 -e signed-integer -t raw -r ' + str(Fs) + ' - -t wav -r ' + str(Fs) + ' ' + gen_path + basefilename + '_synthesized_based_on_residual_0.wav'
    ###print(command)
    run(command, shell=True)
    
    command = "sox -G " + gen_path + basefilename + '_synthesized_based_on_residual_0.wav' + ' ' + \
        gen_path + basefilename + '_synthesized_based_on_residual_upper.wav'
    ###print(command)
    run(command, shell=True)    
   
    # lower frequency band
    scaled_source = np.float32(source_lower / np.max(np.abs(source_lower)) )
    io_wav.write(gen_path + basefilename + '_residual_lower_float32.wav', Fs, scaled_source)
    
    command = 'sox ' + gen_path + basefilename + '_residual_lower_float32.wav' + ' -t raw -r ' + str(Fs) + ' - ' + ' | ' + \
              'mglsadf -P 5 -m ' + str(order) + ' -p ' + str(frshft) + \
              ' -a ' + str(alpha) + ' -c ' + str(stage) + ' ' + gen_path + basefilename + '.mgc' + ' | ' + \
              'sptk x2x +fs -o | sox -c 1 -b 16 -e signed-integer -t raw -r ' + str(Fs) + ' - -t wav -r ' + str(Fs) + ' ' + gen_path + basefilename + '_synthesized_based_on_residual_0.wav'
    run(command, shell=True)
    
    command = "sox -G " + gen_path + basefilename + '_synthesized_based_on_residual_0.wav' + ' ' + \
        gen_path + basefilename + '_synthesized_based_on_residual_lower.wav'
    run(command, shell=True)
       
    # upper and lower frequency band added together
    source = source_lower + source_upper
    scaled_source = np.float32(source / np.max(np.abs(source)) )
    io_wav.write(gen_path + basefilename + '_residual_float32.wav', Fs, scaled_source)
    
    command = 'sox ' + gen_path + basefilename + '_residual_float32.wav' + ' -t raw -r ' + str(Fs) + ' - ' + ' | ' + \
              'mglsadf -P 5 -m ' + str(order) + ' -p ' + str(frshft) + \
              ' -a ' + str(alpha) + ' -c ' + str(stage) + ' ' + gen_path + basefilename + '.mgc' + ' | ' + \
              'sptk x2x +fs -o | sox -c 1 -b 16 -e signed-integer -t raw -r ' + str(Fs) + ' - -t wav -r ' + str(Fs) + ' ' + gen_path + basefilename + '_synthesized_based_on_residual_0.wav'
    ###print(command)
    run(command, shell=True)
    
    command = "sox -G " + gen_path + basefilename + '_synthesized_based_on_residual_0.wav' + ' ' + \
        gen_path + basefilename + '_synthesized_based_on_residual.wav'
    run(command, shell=True)
    
    return [0]

#############################################   Temporal envelope  ##################################################

def triangular (z, a, b, c):
    
    y = np.zeros(z.shape)
    y[z <= a] = 0
    y[z >= c] = 0

    # First half triangular
    first_half = np.logical_and(a < z, z <= b)
    y[first_half] = (z[first_half]-a) / (b-a)

    # Second half triangular
    second_half = np.logical_and(b < z, z < c)
    y[second_half] = (c-z[second_half]) / (c-b)
    return y

# envelope_type:
# - Amplitude Envelope
# - Hilbert Envelope
# - Triangular Envelope
# - True Envelope
def apply_envelope(signal, envelope_type):
    residual_frame = signal.copy()
    
    if envelope_type == 'Amplitude':
        residual_frame_abs = np.abs(residual_frame)
        N = 10 # filter order
        amplitude_envelope = residual_frame_abs / (2 * N + 1) # Previous
        residual_frame_with_envelope = amplitude_envelope
    
        
    elif envelope_type == 'Hilbert':        
        analytic_signal = scipy.signal.hilbert(residual_frame)
        residual_frame_with_envelope = np.abs(analytic_signal)
        
              
    elif envelope_type == 'Triangular':
        a = 0.35 * len(residual_frame)
        c = 0.65 * len(residual_frame)
        b = (a + c) / 2
        z = np.linspace(0, len(residual_frame), len(residual_frame))
        residual_frame_triang = triangular(z, a, b, c)
        residual_frame_with_envelope = residual_frame_triang
        
        
    elif envelope_type == 'True':
        residual_frame_fft_cep = fft(residual_frame)
        residual_frame_abs_cep =  np.abs(residual_frame_fft_cep)
        residual_frame_log_cep = 20 * np.log10(residual_frame_abs_cep)
        residual_frame_ifft = ifft(residual_frame_log_cep)
        residual_frame_ifft_cep = np.abs(residual_frame_ifft)
        c = residual_frame_ifft_cep
        # True envelope:
        residual_frame_fft = fft(residual_frame)
        w = 20 # weight
        residual_frame_log =  10 * np.log10(residual_frame_fft)
        TE = residual_frame_log           
        for k in range (0, 100):
            TE[k] = max(TE[k], c[k-1])
        residual_frame_ifft = ifft(w * TE)
        residual_frame_with_envelope = residual_frame_ifft
        
    else:
        raise ValueError('Wrong envelope type!')
    
    return residual_frame_with_envelope


#######################################  mgc decoder  ##########################################################


def mgc_decoder_residual_with_envelope(pitch, mvf, mgc_coeff, resid_codebook_pca, basefilename, envelope_type):
    
    # create voiced source excitation using SPTK
    source_voiced = pysptk.excite(Fs / pitch, frshft)
    
    # create unvoiced source excitation using SPTK
    pitch_unvoiced = np.zeros(len(pitch))
    source_unvoiced = pysptk.excite(pitch_unvoiced, frshft)
    
    source = np.zeros(source_voiced.shape)
    
    # generate excitation frame by frame pitch synchronously
    for i in range(len(source)):
        if source_voiced[i] > 2: # location of impulse in original impulse excitation
            mvf_index = int(i / frshft)
            mvf_curr = mvf[mvf_index]
            
            if mvf_curr > 7500:
                mvf_curr = 7500
            
            # voiced component from binary codebook
            voiced_frame_lpf = resid_codebook_pca[int((Fs / 2 - 0.95 * mvf_curr) / 100)]
            
            # unvoiced component by highpass filtering white noise
            if i + frlen < len(source_unvoiced):
                unvoiced_frame = source_unvoiced[i : i + len(voiced_frame_lpf)].copy()
            else:
                unvoiced_frame = source_unvoiced[i - len(voiced_frame_lpf) : i].copy()
            
            unvoiced_frame_hpf = highpass_filter(unvoiced_frame, mvf_curr * 1.05, Fs, hpf_order)
            unvoiced_frame_hpf *= np.hanning(len(unvoiced_frame_hpf))
            
            # unvoiced component multiplied with time envelope
            unvoiced_frame_with_envelope = unvoiced_frame.copy() * apply_envelope(resid_codebook_pca[0], envelope_type)
            unvoiced_frame_with_envelope_hpf = highpass_filter(unvoiced_frame_with_envelope, mvf_curr * 1.05, Fs, hpf_order)
            unvoiced_frame_with_envelope_hpf *= np.hanning(len(unvoiced_frame_with_envelope_hpf))
            
            energy = np.linalg.norm(unvoiced_frame_with_envelope_hpf)
            unvoiced_frame_with_envelope_hpf /= energy
            
            # scale time envelope modulated noise by mvf
            unvoiced_frame_with_envelope_hpf *= (mvf_curr / 8000 * 2)
            
            
            
            # put voiced and unvoiced component to pitch synchronous location
            j_start = np.max((round(len(voiced_frame_lpf) / 2) - i, 0))
            j_end   = np.min((len(voiced_frame_lpf), len(source) - (i - round(len(voiced_frame_lpf) / 2))))
            for j in range(j_start, j_end):
                source[i - round(len(voiced_frame_lpf) / 2) + j] += voiced_frame_lpf[j]
                source[i - round(len(voiced_frame_lpf) / 2) + j] += unvoiced_frame_hpf[j] * noise_scaling
                source[i - round(len(voiced_frame_lpf) / 2) + j] += unvoiced_frame_with_envelope_hpf[j]
                
    # scale for SPTK
    scaled_source = np.float32(source / np.max(np.abs(source)) )
    # scaled_source = np.float32(source)
    io_wav.write(gen_path + basefilename + '_source_' + envelope_type + '_float32.wav', Fs, scaled_source)
    
    command = 'sox ' + gen_path + basefilename + '_source_' + envelope_type + '_float32.wav' + ' -t raw -r ' + str(Fs) + ' - ' + ' | ' + \
              'mglsadf -P 5 -m ' + str(order) + ' -p ' + str(frshft) + \
              ' -a ' + str(alpha) + ' -c ' + str(stage) + ' ' + gen_path + basefilename + '.mgc' + ' | ' + \
              'sptk x2x +fs -o | sox -c 1 -b 16 -e signed-integer -t raw -r ' + str(Fs) + ' - -t wav -r ' + str(Fs) + ' ' + gen_path + basefilename + '_synthesized_with_' + envelope_type + '_0.wav'
    run(command, shell=True)
    
    command = "sox -G " + gen_path + basefilename + '_synthesized_with_' + envelope_type + '_0.wav' + ' ' + \
        gen_path + basefilename + '_synthesized_with_' + envelope_type + '.wav ' + 'gain -n 0'
    run(command, shell=True)
   
    return [0]


################################## Main program ############################################################################



# encode all files
for wav_file in os.listdir(gen_path):
    if '.wav' in wav_file and 'synthesized' not in wav_file and 'source' not in wav_file and 'residual' not in wav_file:
        basefilename = wav_file[:-4]
        print('starting encoding of file: ' + basefilename) 
        
# read in residual PCA codebook and filtered version
resid_codebook_pca = read_residual_codebook(codebook_filename)


# decode all files
for lf0_file in os.listdir(gen_path):
    if '.lf0' in lf0_file: # and '088' in lf0_file:
        basefilename = lf0_file[:-4]
        print('starting encoding of file: ' + basefilename)

        
        if not os.path.exists(gen_path + basefilename + '.lf0'):
            get_pitch(gen_path, basefilename)
        if not os.path.exists(gen_path + basefilename + '.mvf'):
            get_MVF(gen_path, basefilename)

            
        # open pitch, MVF , MGC
        lf0 = np.float64(np.fromfile(gen_path + basefilename + '.lf0', dtype=np.float32))
        pitch = np.exp(lf0)
        lmvf = np.float64(np.fromfile(gen_path + basefilename + '.mvf', dtype=np.float32))
        mvf = np.exp(lmvf)
        mgc_coeff = [0]


        
        length = np.min([len(pitch), len(mvf)])
        pitch = pitch[0:length]
        mvf = mvf[0:length]

        
        # run pulsenoise decoder (for benchmark) and write to file
        mgc_decoder_pulsenoise(pitch, mvf, mgc_coeff, resid_codebook_pca, basefilename)
        
        # run decoder with envelopes
        for envelope in envelopes:
            print('starting decoding of file: ' + basefilename + ' with envelope: ' + envelope)
            mgc_decoder_residual_with_envelope(pitch, mvf, mgc_coeff, resid_codebook_pca, basefilename, envelope)
            

os.system('rm '+sys.argv[1]+'/*_float32.wav')
os.system('rm '+sys.argv[1]+'/*_pulsenoise.wav')
os.system('rm '+sys.argv[1]+'/*_0.wav')






