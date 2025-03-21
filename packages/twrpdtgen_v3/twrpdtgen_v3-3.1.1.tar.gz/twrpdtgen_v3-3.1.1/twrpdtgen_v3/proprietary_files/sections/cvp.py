#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class CvpSection(Section):
	name = "CVP"
	interfaces = [
		"vendor.qti.hardware.cvp",
	]

class CvpFirmwareSection(Section):
	name = "CVP firmware"
	patterns = [
		"(.*/)?firmware/evass\..*",
		"(.*/)?firmware/evass-lt\..*",
	]

register_section(CvpSection)
register_section(CvpFirmwareSection)
