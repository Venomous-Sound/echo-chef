# chefbot_file_utils.py

import os
import math
from pydub import AudioSegment

MAX_DISCORD_SIZE_MB = 8


    
def is_file_too_large(file_path, limit_mb=MAX_DISCORD_SIZE_MB):
    size_mb = os.path.getsize(file_path) / (1024 * 1024)
    return size_mb > limit_mb, round(size_mb, 2)

def split_mp3(file_path, target_size_mb=MAX_DISCORD_SIZE_MB):
    audio = AudioSegment.from_mp3(file_path)
    total_size = os.path.getsize(file_path) / (1024 * 1024)
    num_chunks = math.ceil(total_size / target_size_mb)

    chunk_duration_ms = len(audio) / num_chunks
    output_files = []
    base = os.path.splitext(file_path)[0]
    # Rename original file to preserve it before splitting
    if os.path.exists(file_path):
        part1_path = f"{base}_part1.mp3"
        os.rename(file_path, part1_path)
        output_files.append(part1_path)
    for i in range(num_chunks):
        start = int(i * chunk_duration_ms)
        end = int((i + 1) * chunk_duration_ms)
        chunk = audio[start:end]
        output_path = f"{base}_part{i+2}.mp3"
        chunk.export(output_path, format="mp3")
        output_files.append(output_path)
    return output_files

def convert_wav_to_mp3(wav_path):
    from pydub import AudioSegment
    mp3_path = wav_path.replace('.wav', '.mp3')
    audio = AudioSegment.from_wav(wav_path)
    audio.export(mp3_path, format="mp3")
    return mp3_path

def convert_m4a_to_mp3(m4a_path):
    from pydub import AudioSegment
    mp3_path = m4a_path.replace('.m4a', '.mp3')
    audio = AudioSegment.from_file(m4a_path, format="m4a")
    audio.export(mp3_path, format="mp3")
    return mp3_path
