#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class TetherOffloadSection(Section):
	name = "Tether offload"
	interfaces = [
		"android.hardware.tetheroffload",
		"android.hardware.tetheroffload.config",
		"android.hardware.tetheroffload.control",
	]
	binaries = [
		"tetheroffloadservice",
	]

register_section(TetherOffloadSection)
