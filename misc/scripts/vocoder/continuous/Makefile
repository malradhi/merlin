.PHONY: build continuous_vocoder

all: build

build: continuous_vocoder build_sigproc

build_sigproc: continuous_vocoder
	@chmod u+x *.sh
	@chmod u+x spec_env
	@./run_continuous_vocoder.sh