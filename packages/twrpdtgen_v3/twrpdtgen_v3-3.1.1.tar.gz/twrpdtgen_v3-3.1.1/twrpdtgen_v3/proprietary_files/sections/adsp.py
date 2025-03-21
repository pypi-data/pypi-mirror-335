#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class AdspSection(Section):
	name = "ADSP"
	interfaces = [
		"vendor.qti.adsprpc",
	]
	binaries = [
		"adsprpcd",
	]
	libraries = [
		"libadsprpc",
		"libadsp_default_listener",
	]

class AdspModulesSection(Section):
	name = "ADSP modules"
	folders = [
		"lib/rfs/dsp",
		"lib/rfsa/adsp",
		"lib64/rfs/dsp",
		"lib64/rfsa/adsp",
	]

register_section(AdspSection)
register_section(AdspModulesSection)
