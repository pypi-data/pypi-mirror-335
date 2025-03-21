#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class CdspSection(Section):
	name = "CDSP"
	interfaces = [
		"vendor.qti.cdsprpc",
	]
	binaries = [
		"cdsprpcd",
	]
	libraries = [
		"libcdsprpc",
		"libcdsp_default_listener",
		"libfastcvdsp_stub",
		"libfastcvopt",
	]

register_section(CdspSection)
