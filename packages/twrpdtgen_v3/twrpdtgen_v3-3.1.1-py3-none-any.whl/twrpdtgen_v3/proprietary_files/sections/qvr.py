#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class QvrSection(Section):
	name = "QVR"
	interfaces = [
		"vendor.qti.hardware.qvr",
	]
	binaries = [
		"qvrdatalogger",
		"qvrservice",
		"qvrservicetest",
		"qvrservicetest64",
	]
	folders = [
		"etc/qvr",
	]

register_section(QvrSection)
