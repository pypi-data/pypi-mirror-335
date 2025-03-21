#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class ServicetrackerSection(Section):
	name = "Service tracker"
	interfaces = [
		"vendor.qti.hardware.servicetracker",
	]

register_section(ServicetrackerSection)
