#!/usr/bin/env python3
import os
import sys
from base64 import standard_b64encode


ESC = b"\x1b_G"
ST = b"\x1b\\"


def icat(path: str, chunk_size: int = 4096) -> None:
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    with open(path, "rb") as f:
        data = standard_b64encode(f.read())

    out = sys.stdout.buffer

    for offset in range(0, len(data), chunk_size):
        chunk = data[offset:offset + chunk_size]

        first = offset == 0
        last = offset + chunk_size >= len(data)

        params = []

        if first:
            params += [
                "a=T",    # transmit and display
                "f=100",  # PNG
                "q=2",    # suppress kitty replies
            ]

        params.append(f"m={0 if last else 1}")

        out.write(ESC + ",".join(params).encode("ascii") + b";" + chunk + ST)

    # Important: prevents zsh from printing its ugly "%" partial-line marker
    out.write(b"\n")
    out.flush()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: icat.py <image.png>", file=sys.stderr)
        sys.exit(1)

    icat(sys.argv[1])
