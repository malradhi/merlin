function MaximumVoicedFrequencyEstimation_nopp_run(filename_wav, filename_lf0i, filename_mvfi)

Fs = 16000;
frlen = 0.025 * Fs;
frshft = 0.005 * Fs;

% disp(['inputs: ' filename_wav ' ' filename_lf0i ' ' filename_mvfi]);

% check whether Fs == 16000 Hz
if (exist(filename_wav, 'file'))
    [wav, Fs_orig] = audioread(filename_wav);
	if (Fs_orig ~= 16000)
		disp(['Sampling frequency is not ' num2str(Fs) ' Hz!']);
		return;
	end
else
    disp([filename_wav ' file not available!']);
    return;
end


% disp('Calculating MVFI using AS_IHPC');

% read pitch file
if (exist(filename_lf0i, 'file'))
	fid = fopen(filename_lf0i);
	lf0i = fread(fid, 'float');
	fclose(fid);
	pitchi = exp(lf0i);
else
    disp([filename_lf0i ' file not available!']);
    return;
end


% fix pitch vector length
pitch_times = round((0 : (length(pitchi) - 1)) * frshft + frlen / 2);
while (pitch_times(end) > length(wav) - frshft)
	pitch_times = pitch_times(1:end-1);
end
pitch_times = pitch_times(1:end-1);


% calculate MVF
[AS_IHPC, ~, ~, ~, ~] = MaximumVoicedFrequencyEstimation_nopp(wav, Fs, pitchi, pitch_times');

mvfi = AS_IHPC;    
mvfi = log(mvfi);
if (sum(isinf(mvfi)) > 0 || sum(isnan(mvfi)) > 0)
	disp('Inf or NaN value in MVFI!');
	return;
end

fid = fopen(filename_mvfi, 'w');
fwrite(fid, mvfi, 'float');
fclose(fid);

% make lf0i and mvfi to equal length
% if (length(lf0i) > length(mvfi))
	% fid = fopen([basefilename '.lf0i'], 'w');
	% fwrite(fid, lf0i(1:length(mvfi)), 'float');
	% fclose(fid);
% end
