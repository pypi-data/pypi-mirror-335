#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class BootSection(Section):
	name = "Boot"
	interfaces = [
		"android.hardware.boot",
	]

register_section(BootSection)
