import os
import torchaudio
import glob
import torch

input_dir = './audios_all'
output_dir = './audio_all_compressed'

os.makedirs(output_dir, exist_ok=True)

audio_list = sorted(glob.glob(os.path.join(input_dir, '*')))
for i in audio_list:
    audio, sr = torchaudio.load(i)
    downsample_resample = torchaudio.transforms.Resample(
        sr, 16000, resampling_method='sinc_interpolation')

    audio_down = downsample_resample(audio)
    output_path = os.path.join(output_dir, os.path.basename(i))
    torchaudio.save(output_path, torch.clamp(audio_down, -1, 1), 16000, precision=32)

 