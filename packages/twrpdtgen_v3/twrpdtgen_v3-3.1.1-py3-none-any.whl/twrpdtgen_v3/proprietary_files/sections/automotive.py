#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class AutomotiveSection(Section):
	name = "Automotive"
	interfaces = [
		"android.hardware.automotive.audiocontrol",
		"android.hardware.automotive.can",
		"android.hardware.automotive.evs",
		"android.hardware.automotive.occupant_awareness",
		"android.hardware.automotive.sv",
		"android.hardware.automotive.vehicle",
		"vendor.qti.hardware.automotive.vehicle",
	]

register_section(AutomotiveSection)
