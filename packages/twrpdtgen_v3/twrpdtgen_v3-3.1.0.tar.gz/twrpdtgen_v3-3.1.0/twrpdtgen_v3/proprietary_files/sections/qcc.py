#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class QccSection(Section):
	name = "QCC"
	interfaces = [
		"vendor.qti.hardware.qccsyshal",
		"vendor.qti.hardware.qccvndhal",
		"vendor.qti.qccvndhal_aidl",
	]
	binaries = [
		"qcc-vendor",
	]

register_section(QccSection)
