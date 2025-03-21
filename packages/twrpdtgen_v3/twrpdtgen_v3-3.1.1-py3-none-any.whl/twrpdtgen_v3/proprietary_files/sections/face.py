#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class FaceSection(Section):
	name = "Face"
	interfaces = [
		"android.hardware.biometrics.face",
		"vendor.oplus.hardware.biometrics.face",
	]

register_section(FaceSection)
