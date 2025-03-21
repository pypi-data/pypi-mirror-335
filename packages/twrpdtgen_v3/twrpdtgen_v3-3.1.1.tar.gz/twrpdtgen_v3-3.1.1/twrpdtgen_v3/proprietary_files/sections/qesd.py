#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class QesdSection(Section):
	name = "QESD"
	interfaces = [
		"vendor.qti.qesdhal",
		"vendor.qti.qesdhalaidl",
		"vendor.qti.qesdsys",
	]
	binaries = [
		"perf_qesdk_client",
		"qesdk-manager",
		"sensors-qesdk",
	]

register_section(QesdSection)
