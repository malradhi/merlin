# Continuous Vocoder
It is a system for speech analysis and synthesis. It can estimate continuous parameters: Fundamental frequency (F0), maximum voiced frequency (MVF) and spectral envelope (MGC). It also generate the speech like input speech using only 3 estimated continuous parameters with lower dimensions.

* Continuous vocoder can be used for Statistical Parametric Speech Synthesis (SPSS), Text-to-Speech (TTS), and Voice Conversion (VC).



### Requirements:

- Sox
- SPTK
- Octave
- Python 3
- Python packages: numpy, scipy, pysptk, ssp, struct



### Install

```
$ git clone https://github.com/malradhi/continuous-vocoder.git
```


### Testing / HowTo

In the root directory, simply run:

```
$ make
```

You can also have a look at the file **cont_features_extraction.py** and **cont_speech_synthesis.py** to see how the continuous vocoder can work.



### Legal
Copyright(C) 2020 Department of Telecommunications and Media informatics, Speech Communication and Smart Interactions Laboratory, Budapest University of Technology and Economics, Hungary.
> http://smartlab.tmit.bme.hu/index-en



### Demo
Audio samples are also available in English and Arabic (with emotions) at http://smartlab.tmit.bme.hu/vocoder_Arabic_2018

 

### References

*This system is based on the method described in the papers:*

[1] Mohammed Salah Al-Radhi, Tamás Gábor Csapó, Géza Németh, Time-domain envelope modulating the noise component of excitation in a continuous residual-based vocoder for statistical parametric speech synthesis, in Proceedings of the 18th Interspeech conference, pp. 434-438, Stockholm, Sweeden, 2017. https://www.doi.org/10.21437/Interspeech.2017-678

[2] Mohammed Salah Al-Radhi, Omnia Abdo, Tamás Gábor Csapó, Sherif Abdou, Géza Németh, Mervat Fashal, A continuous vocoder for statistical parametric speech synthesis and its evaluation using an audio-visual phonetically annotated Arabic corpus, Computer Speech and Language, ScienceDirect Elsevier, 60, 2019. https://doi.org/10.1016/j.csl.2019.101025

[3] Tamás Gábor Csapó, Géza Németh, Cernak M., "Residual-Based Excitation with Continuous F0 Modeling in HMM-Based Speech Synthesis," In Proceedings of the 3rd International Conference on Statistical Language and Speech Processing (SLSP), Budapest, Hungary, vol. 9449, pp. 27-38, 2015. https://doi.org/10.1007/978-3-319-25789-1_4
