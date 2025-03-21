#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class TrustedUiSection(Section):
	name = "Trusted UI"
	interfaces = [
		"vendor.qti.hardware.trustedui",
		"vendor.qti.hardware.tui_comm",
		"vendor.trustonic.tee.tui",
	]
	binaries = [
		"TrustedUISampleTest",
	]
	libraries = [
		"libTrustedUI",
		"libTrustedUIAIDL",
		"libTrustedUITZ",
		"libTrustedUIVM",
	]

register_section(TrustedUiSection)
