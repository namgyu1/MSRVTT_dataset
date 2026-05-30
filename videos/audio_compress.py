import torchaudio
import glob
import torch

audio_list = sorted(glob.glob('./audios_all/*'))
for i in audio_list:
        audio, sr = torchaudio.load(i)
        downsample_resample = torchaudio.transforms.Resample(
            sr, 16000, resampling_method='sinc_interpolation')

        audio_down = downsample_resample(audio)
        torchaudio.save('./audio_all_compressed'+i[12:], torch.clamp(audio_down, -1, 1), 16000, precision=32)

 