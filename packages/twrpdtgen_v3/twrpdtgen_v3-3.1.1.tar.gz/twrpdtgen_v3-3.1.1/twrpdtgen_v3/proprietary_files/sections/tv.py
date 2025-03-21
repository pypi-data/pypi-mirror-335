#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class TvSection(Section):
	name = "TV"
	interfaces = [
		"android.hardware.tv.cec",
		"android.hardware.tv.input",
		"android.hardware.tv.tuner",
	]
	hardware_modules = [
		"tv_input",
	]

register_section(TvSection)
