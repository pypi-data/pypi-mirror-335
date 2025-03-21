#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class CitSection(Section):
	name = "CIT"
	interfaces = [
		"vendor.xiaomi.cit.bluetooth",
		"vendor.xiaomi.cit.wifi",
		"vendor.xiaomi.hardware.citsensorservice",
		"vendor.xiaomi.hardware.citvendorservice",
	]

register_section(CitSection)
