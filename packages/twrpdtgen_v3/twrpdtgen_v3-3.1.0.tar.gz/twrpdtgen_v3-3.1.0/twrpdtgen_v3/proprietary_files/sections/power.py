#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class PowerSection(Section):
	name = "Power"
	interfaces = [
		"android.hardware.power",
		"vendor-oplus-hardware-power-powermonitor",
		"vendor.qti.hardware.power.powermodule",
		"vendor.mediatek.hardware.mtkpower",
	]
	hardware_modules = [
		"power",
	]
	properties_prefixes = {
		"vendor.power.": False,
	}

class PowerConfigsSection(Section):
	name = "Power configs"
	folders = [
		"etc/pwr",
	]

register_section(PowerSection)
register_section(PowerConfigsSection)
