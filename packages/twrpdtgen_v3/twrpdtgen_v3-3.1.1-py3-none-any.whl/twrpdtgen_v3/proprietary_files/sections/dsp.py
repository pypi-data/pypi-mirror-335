#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class DspSection(Section):
	name = "DSP"
	interfaces = [
		"vendor.qti.hardware.dsp",
	]
	binaries = [
		"dspservice",
	]
	filenames = [
		"vendor.qti.hardware.dsp.policy",
	]

register_section(DspSection)
