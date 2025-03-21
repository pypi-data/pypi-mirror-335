#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class VibratorSection(Section):
	name = "Vibrator"
	interfaces = [
		"android.hardware.vibrator",
		"motorola.hardware.vibrator",
		"vendor.asus.vibrator.vibratorgovern",
		"vendor.oplus.hardware.vibrator",
		"vendor.qti.hardware.vibrator",
		"vendor.xiaomi.hardware.vibratorfeature",
	]
	hardware_modules = [
		"vibrator",
	]

class VibratorFirmwareSection(Section):
	name = "Vibrator firmware"
	folders = [
		"etc/vibrator",
	]
	patterns = [
		"(.*/)?firmware/.*(rtp|RTP)\.bin",
		"(.*/)?firmware/aw8622x.*\.bin",
		"(.*/)?firmware/aw8697.*\.bin",
	]

register_section(VibratorSection)
register_section(VibratorFirmwareSection)
