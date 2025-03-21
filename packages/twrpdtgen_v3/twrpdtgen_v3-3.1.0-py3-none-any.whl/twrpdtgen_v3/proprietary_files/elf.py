#
#
# Copyright (C) 2025 The LineageOS Project
#
# Copyright (C) 2025 xXHenneBXx
#
# SPDX-License-Identifier: Apache-2.0
#

from pathlib import Path
from typing import List

def get_shared_libs(files: List[Path]):
	for lib in files:
		if not lib.suffix == ".so":
			continue

		yield lib
