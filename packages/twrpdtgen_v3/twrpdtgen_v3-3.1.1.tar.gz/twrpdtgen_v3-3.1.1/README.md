# twrpdtgen_v3

[![PyPI version](https://img.shields.io/pypi/v/twrpdtgen_v3)](https://pypi.org/project/twrpdtgen_v3/)

Create a TWRP-compatible device tree from an Android stock ROM dump (made with [dumpyara](https://github.com/SebaUbuntu/dumpyara)).
This script supports any Android firmware from a Treble-enabled device (Higher than Android 8.0 and with VNDK enabled, you can check it with [Treble Info](https://play.google.com/store/apps/details?id=tk.hack5.treblecheck) or with `adb shell getprop ro.treble.enabled`).
For pre-Treble devices please use [twrpdtgen](https://github.com/twrpdtgen/twrpdtgen).

Requires Python 3.8 or greater

## Installation

```sh
pip3 install twrpdtgen_v3
```

## Instructions

```
$ python3 -m twrpdtgen_v3 -h
Android device tree generator
Version 3.1.0

usage: python3 -m twrpdtgen_v3 [-h] [-o OUTPUT] dump_path

positional arguments:
  dump_path             path to an Android dump made with dumpyara

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        custom output folder
```

## License

```
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#
```
