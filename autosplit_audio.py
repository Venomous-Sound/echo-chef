import os
import math
from pydub import AudioSegment
import shutil

if not shutil.which("ffmpeg"):
    raise EnvironmentError("❌ ffmpeg is not installed or not found in PATH. Please install ffmpeg to use this tool.")

MAX_FILE_SIZE_MB = 8

def split_mp3(file_path, target_size_mb=MAX_FILE_SIZE_MB):
    audio = AudioSegment.from_mp3(file_path)
    total_size = os.path.getsize(file_path) / (1024 * 1024)
    if total_size <= target_size_mb:
        print(f"✅ File is under {target_size_mb}MB. No need to split.")
        return [file_path]

    num_chunks = math.ceil(total_size / target_size_mb)
    chunk_duration_ms = len(audio) / num_chunks
    output_files = []

    for i in range(num_chunks):
        start = int(i * chunk_duration_ms)
        end = int((i + 1) * chunk_duration_ms)
        chunk = audio[start:end]
        chunk_filename = f"{file_path}_part{i+1}.mp3"
        chunk.export(chunk_filename, format="mp3")
        output_files.append(chunk_filename)
        print(f"💾 Exported: {chunk_filename}")

    return output_files

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto-split MP3 files if they exceed size limit.")
    parser.add_argument("file_path", help="Path to the MP3 file")
    args = parser.parse_args()

    split_files = split_mp3(args.file_path)
    print(f"\n🎉 Done! Created {len(split_files)} part(s):")
    for f in split_files:
        print(f" - {f}")
