#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class AlarmSection(Section):
	name = "Alarm"
	interfaces = [
		"vendor.qti.hardware.alarm",
	]
	apps = [
		"PowerOffAlarm",
	]
	binaries = [
		"power_off_alarm",
		"poweroffm64",
	]

register_section(AlarmSection)
