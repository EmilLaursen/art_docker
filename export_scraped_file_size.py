#!/usr/bin/env python3
import plac
from pathlib import Path


mib = 1024 ** 2


def main(
    file_ext: ("The file extension to process.", "option", "e"),
    inp: ("The directory to search.", "option", "d"),
    output: ("The file to write metrics.", "option", "o"),
):
    ext = "." + file_ext

    p = Path(inp)

    files = [
        content
        for content in p.iterdir()
        if content.suffix == ext and content.is_file()
    ]

    file_size_dict = {file.name: file.stat().st_size / mib for file in files}

    out = Path(output)
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        out.touch()

    with out.open(mode="w") as writer:
        for fname, size in file_size_dict.items():
            writer.write(
                'scraped_file_size{directory="'
                + fname
                + '"} '
                + "{:.1f}".format(size)
                + "\n"
            )


if __name__ == "__main__":
    plac.call(main)
