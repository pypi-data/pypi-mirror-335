#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class DpmSection(Section):
	name = "DPM"
	interfaces = [
		"com.qualcomm.qti.dpm.api",
		"vendor.qti.diaghal",
		"vendor.qti.hardware.dpmaidlservice",
		"vendor.qti.hardware.dpmservice",
	]
	binaries = [
		"dpmQmiMgr",
		"dpmd",
	]
	folders = [
		"etc/dpm",
	]
	properties_prefixes = {
		"persist.vendor.dpm.": False,
		"persist.vendor.dpmhalservice.": False,
	}

register_section(DpmSection)
