#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class InputSection(Section):
	name = "Input"
	interfaces = [
		"android.hardware.input.classifier",
		"android.hardware.input.common",
		"android.hardware.input.processor",
	]

class InputMotorolaSection(Section):
	name = "Input (Motorola)"
	interfaces = [
		"motorola.hardware.input",
	]

register_section(InputSection)
register_section(InputMotorolaSection)
