import argparse
import json
import os
import subprocess

from tqdm import tqdm

try:
    from pytube import YouTube
except ImportError:
    YouTube = None


def parse_args():
    parser = argparse.ArgumentParser(description="Build audios_all from local MSRVTT videos or video URLs.")
    parser.add_argument("--data_path", default="./MSRVTT_data.json", help="MSRVTT metadata json path")
    parser.add_argument("--dest", default="./videos/audios_all", help="output wav directory")
    parser.add_argument("--source", choices=["local", "youtube"], default="local", help="audio source")
    parser.add_argument("--video_path", default="./videos/all", help="raw video directory for local mode")
    parser.add_argument("--error_log", default="./err_vid.txt", help="failed video id log path")
    return parser.parse_args()


def load_metadata(data_path):
    with open(data_path, "r") as handle:
        data = json.load(handle)
    return data["videos"]


def extract_audio_segment(input_path, start_time, end_time, output_path):
    command = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start_time),
        "-to",
        str(end_time),
        "-i",
        input_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        output_path,
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def build_from_local(video_path, video_id, start_time, end_time, output_path):
    input_path = os.path.join(video_path, video_id + ".mp4")
    extract_audio_segment(input_path, start_time, end_time, output_path)


def build_from_youtube(video_url, video_id, start_time, end_time, output_path, output_dir):
    if YouTube is None:
        raise ImportError("pytube is required for --source youtube")
    stream = YouTube(video_url, use_oauth=True).streams.filter(only_audio=True).first()
    download_path = stream.download(output_dir, filename=video_id + "_download")
    extract_audio_segment(download_path, start_time, end_time, output_path)
    if download_path != output_path and os.path.exists(download_path):
        os.remove(download_path)


def main():
    args = parse_args()
    meta_video = load_metadata(args.data_path)
    os.makedirs(args.dest, exist_ok=True)

    with open(args.error_log, "w") as error_handle:
        for item in tqdm(meta_video):
            video_id = item["video_id"]
            output_path = os.path.join(args.dest, video_id + ".wav")
            if os.path.isfile(output_path):
                continue

            try:
                if args.source == "local":
                    build_from_local(args.video_path, video_id, item["start time"], item["end time"], output_path)
                else:
                    build_from_youtube(item["url"], video_id, item["start time"], item["end time"], output_path, args.dest)
            except Exception:
                error_handle.write("{}\n".format(video_id))


if __name__ == "__main__":
    main()
        
    