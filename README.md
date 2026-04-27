# icat.py 🐈

<img width="770" height="1114" alt="2026-04-27-150842_hyprshot" src="https://github.com/user-attachments/assets/f61f2871-dbac-4d29-86c1-f83f66c708f1" />

A tiny Python implementation of kitty’s terminal graphics protocol for displaying PNG images directly inside a kitty-compatible terminal.

This is basically a minimal `icat` clone: pass it an image path, and it prints the correct escape sequences so the image appears inline in your terminal.

## Features

- Displays PNG images directly in the terminal
- Uses kitty graphics protocol
- Streams image data in chunks
- Handles multi-chunk transmission correctly with `m=1` / `m=0`
- Suppresses kitty protocol replies for cleaner output
- Adds a trailing newline to avoid zsh’s ugly `%` marker

## Requirements

- Python 3
- A terminal that supports the kitty graphics protocol

Tested with:

- `kitty`
- terminals implementing kitty graphics protocol compatibility

## Installation

Clone or copy the script:

```bash
git clone <your-repo-url>
cd <your-repo>
chmod +x icat.py
````

Or just run it directly with Python:

```bash
python3 icat.py image.png
```

## Usage

```bash
./icat.py <image.png>
```

Example:

```bash
./icat.py arch_input.png
```

You should see the image rendered directly inside your terminal.

## Supported Formats

Currently this script assumes the input file is a **PNG**.

That is because it sends:

```text
f=100
```

which means PNG in the kitty graphics protocol.

For JPEG, WebP, or other formats, convert them first:

```bash
magick input.jpg output.png
./icat.py output.png
```

or:

```bash
ffmpeg -i input.webp output.png
./icat.py output.png
```

## How It Works

The script reads the image as bytes, encodes it as base64, then sends it to the terminal using kitty graphics escape sequences:

```text
ESC_G ... ; <base64 data> ESC\
```

Large images are split into chunks. Kitty needs to know whether more chunks are coming:

```text
m=1
```

means more chunks follow.

```text
m=0
```

means this is the final chunk.

The first chunk includes metadata:

```text
a=T,f=100,q=2
```

Where:

| Parameter | Meaning                        |
| --------- | ------------------------------ |
| `a=T`     | transmit and display the image |
| `f=100`   | image format is PNG            |
| `q=2`     | suppress terminal replies      |
| `m=1`     | more chunks follow             |
| `m=0`     | final chunk                    |

## Why Was There a `%` After the Image?

If you use zsh, you may see a `%` after commands that do not end with a newline.

That is not part of the image. It is zsh’s partial-line marker.

This script fixes that by writing a newline after the image is displayed:

```python
out.write(b"\n")
```

## Example Script

```python
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
                "a=T",
                "f=100",
                "q=2",
            ]

        params.append(f"m={0 if last else 1}")

        out.write(ESC + ",".join(params).encode("ascii") + b";" + chunk + ST)

    out.write(b"\n")
    out.flush()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: icat.py <image.png>", file=sys.stderr)
        sys.exit(1)

    icat(sys.argv[1])
```

## Troubleshooting

### Image does not appear

Make sure you are using kitty or a terminal with kitty graphics protocol support.

Check your terminal:

```bash
echo $TERM
```

You usually want something like:

```text
xterm-kitty
```

### I see escape codes instead of an image

Your terminal probably does not support the kitty graphics protocol.

Try running it in kitty:

```bash
kitty
```

Then run:

```bash
./icat.py image.png
```

### JPEG does not work

Convert it to PNG first:

```bash
magick input.jpg output.png
./icat.py output.png
```

### I see a `%` after the image

That usually means the program did not print a trailing newline before exiting. Make sure the script contains:

```python
out.write(b"\n")
```

## Limitations

* PNG only for now
* No image resizing
* No cursor positioning
* No explicit image deletion
* No terminal capability detection
* No support for remote file transfer modes

This is intentionally minimal.

## Future Ideas

* Add JPEG support
* Add automatic conversion through Pillow
* Add width / height options
* Add terminal compatibility checks
* Add `--clear` or image deletion support
* Add stdin support:

```bash
cat image.png | icat.py -
```

## License

MIT License.

Do whatever you want with it, preferably something cursed and terminal-adjacent.
