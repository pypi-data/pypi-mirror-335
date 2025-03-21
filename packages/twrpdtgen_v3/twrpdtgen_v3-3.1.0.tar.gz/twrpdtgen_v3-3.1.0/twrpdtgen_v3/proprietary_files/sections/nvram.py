#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class NVRAMSection(Section):
	name = "NVRAM"
	interfaces = [
		"vendor.mediatek.hardware.nvram",
	]
	binaries = [
		"fuelgauged_nvram",
		"nvram_daemon",
	]
	filenames = [
		"fuelgauged_nvram_init.rc",
	]

register_section(NVRAMSection)

