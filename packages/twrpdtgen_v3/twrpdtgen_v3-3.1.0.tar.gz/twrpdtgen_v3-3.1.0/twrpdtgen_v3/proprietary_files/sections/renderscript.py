#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class RenderscriptSection(Section):
	name = "RenderScript"
	interfaces = [
		"android.hardware.renderscript",
	]
	libraries = [
		"libRSDriver_adreno",
		"librs_adreno",
		"librs_adreno_sha1",
	]

register_section(RenderscriptSection)
