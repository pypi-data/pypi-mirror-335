#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class AntSection(Section):
	name = "ANT"
	interfaces = [
		"com.dsi.ant",
		"com.qualcomm.qti.ant",
		"vendor.xiaomi.hardware.antdtx",
	]

class AntFirmwareSection(Section):
	name = "ANT firmware"
	patterns = [
		"(.*/)?firmware/antdtx\..*",
	]

register_section(AntSection)
register_section(AntFirmwareSection)
