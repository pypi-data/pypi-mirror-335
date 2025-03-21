#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class SecuritySection(Section):
	name = "Security"
	interfaces = [
		"android.hardware.security.keymint",
		"android.hardware.security.rkp",
		"android.hardware.security.secureclock",
		"android.hardware.security.sharedsecret",
	]

register_section(SecuritySection)
