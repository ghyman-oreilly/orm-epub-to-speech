
from pydub import AudioSegment
import os
import shutil
import sys


def check_for_audio_framework(temp_dir):
    if not shutil.which("ffmpeg") and not shutil.which("libav"):
        print("Required audio framework (ffmpeg or libav) not found. Unable to merge chunked audio files.")
        print(f"Nonmerged audio files can be found at {temp_dir}")
        print("Exiting.")
        sys.exit(1)

def merge_audio_files(chunked_audio_list, output_dir, temp_dir):
    """
    Merge MP3 files from chunked_audio_list.

    Args:
        chunked_audio_list: List of lists of tuples:
            - Each nested list represents a section
            - Each tuple is (chunk_index, file_basename, filename)
              All chunks in the section will be merged into file_basename.mp3
        output_dir: output directory
    """
    output = []
    
    check_for_audio_framework(temp_dir)

    os.makedirs(output_dir, exist_ok=True)
    
    for section in chunked_audio_list:               
        if not section:
            continue

        file_basename = section[0][1]  # All entries in the section share the same basename
        output_filename = os.path.join(output_dir, f"{file_basename}.mp3")

        if len(section) == 1:
            # if section isn't chunked, simply save to output folder
            if os.path.exists(section[0][2]):
                shutil.copy(section[0][2], output_filename)
                output.append(output_filename)
            continue

        merged_audio = AudioSegment.empty()

        # Ensure section is sorted by chunk index
        sorted_section = sorted(section, key=lambda tup: tup[0])

        for _, _, filename in sorted_section:
            if os.path.exists(filename):
                audio = AudioSegment.from_file(filename, format="mp3", parameters=["-hide_banner", "-loglevel", "error"])
                merged_audio += audio
            else:
                print(f"Warning: file not found — {filename}")

        # Export the merged audio
        merged_audio.export(
            output_filename,
            format="mp3",
            parameters=["-hide_banner", "-loglevel", "error"]
        )
        output.append(output_filename)

    return output