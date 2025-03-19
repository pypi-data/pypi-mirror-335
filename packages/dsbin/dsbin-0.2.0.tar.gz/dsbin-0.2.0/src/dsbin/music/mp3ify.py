#!/usr/bin/env python3

"""Converts files to MP3."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dsbase.files import list_files
from dsbase.media import MediaManager
from dsbase.text import color as colored
from dsbase.util import dsbase_setup

dsbase_setup()

allowed_extensions = [".aiff", ".aif", ".wav", ".m4a", ".flac"]


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Convert audio files to MP3")
    parser.add_argument(
        "path",
        nargs="?",
        default=str(Path.cwd()),
        help="File or directory of files to convert",
    )
    return parser.parse_args()


def main() -> None:
    """Convert a file to MP3."""
    args = parse_arguments()
    path = args.path

    path = Path(path)
    if path.is_dir():
        files_to_convert = list_files(path, exts=allowed_extensions)
    elif path.is_file() and path.suffix.lower() in allowed_extensions:
        files_to_convert = [path]
    else:
        print(colored("Provided path is neither a supported file nor a directory.", "red"))
        sys.exit(1)

    if not files_to_convert:
        print(colored("No files needing conversion.", "green"))
        sys.exit(0)

    MediaManager().ffmpeg_audio(
        input_files=files_to_convert, output_format="mp3", audio_bitrate="320k", show_output=True
    )


if __name__ == "__main__":
    main()
