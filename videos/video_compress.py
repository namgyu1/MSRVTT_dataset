import argparse
import os
import shutil
import subprocess
from multiprocessing import Pool, cpu_count


def compress(pair):
    input_video_path, output_video_path = pair
    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_video_path,
        "-filter:v",
        "scale='if(gt(a,1),trunc(oh*a/2)*2,224)':'if(gt(a,1),224,trunc(ow*a/2)*2)'",
        "-map",
        "0:v",
        "-r",
        "3",
        output_video_path,
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def prepare_input_output_pairs(input_root, output_root):
    input_video_path_list = []
    output_video_path_list = []
    for root, _, files in os.walk(input_root):
        for file_name in files:
            if not file_name.lower().endswith(".mp4"):
                continue
            input_video_path = os.path.join(root, file_name)
            output_video_path = os.path.join(output_root, file_name)
            if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
                continue
            input_video_path_list.append(input_video_path)
            output_video_path_list.append(output_video_path)
    return input_video_path_list, output_video_path_list


def main():
    parser = argparse.ArgumentParser(description="Compress raw MSRVTT videos into all_compressed.")
    parser.add_argument("--input_root", default="./all", help="raw video directory")
    parser.add_argument("--output_root", default="./all_compressed", help="compressed video directory")
    args = parser.parse_args()

    input_root = args.input_root
    output_root = args.output_root

    if input_root == output_root:
        raise ValueError("input_root and output_root must be different")

    os.makedirs(output_root, exist_ok=True)
    input_video_path_list, output_video_path_list = prepare_input_output_pairs(input_root, output_root)

    print("Total video need to process: {}".format(len(input_video_path_list)))
    with Pool(cpu_count()) as pool:
        pool.map(compress, zip(input_video_path_list, output_video_path_list))

    print("Compress finished, wait for checking files...")
    for input_video_path, output_video_path in zip(input_video_path_list, output_video_path_list):
        if os.path.exists(input_video_path):
            if not os.path.exists(output_video_path) or os.path.getsize(output_video_path) < 1:
                shutil.copyfile(input_video_path, output_video_path)
                print("Copy and replace file: {}".format(output_video_path))


if __name__ == "__main__":
    main()