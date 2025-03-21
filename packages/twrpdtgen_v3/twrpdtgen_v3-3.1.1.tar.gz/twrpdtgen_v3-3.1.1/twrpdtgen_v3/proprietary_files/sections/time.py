#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class TimeSection(Section):
	name = "Time services"
	apps = [
		"TimeService",
	]
	binaries = [
		"time_daemon",
	]
	libraries = [
		"libtime_genoff",
	]

register_section(TimeSection)
