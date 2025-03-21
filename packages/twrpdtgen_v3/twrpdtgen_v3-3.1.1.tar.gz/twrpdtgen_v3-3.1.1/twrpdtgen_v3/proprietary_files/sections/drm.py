#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class DrmSection(Section):
	name = "DRM"
	interfaces = [
		"android.hardware.drm",
	]
	apexes = [
		"com.google.android.widevine.nonupdatable",
	]
	libraries = [
		"liboemcrypto",
	]
	folders = [
		"lib/mediacas",
		"lib/mediadrm",
		"lib64/mediacas",
		"lib64/mediadrm",
	]
	properties_prefixes = {
		"drm.service.enabled": True,
		"ro.netflix.bsp_rev": True,
	}

class DrmQseeSection(Section):
	name = "DRM (Qualcomm Secure Execution Environment)"
	interfaces = [
		"vendor.qti.hardware.qseecom",
	]
	binaries = [
		"qseecomd",
	]
	libraries = [
		"libQSEEComAPI",
	]

class DrmQteeSection(Section):
	name = "DRM (Qualcomm Trusted Execution Environment)"
	interfaces = [
		"vendor.qti.hardware.qteeconnector",
	]
	libraries = [
		"libGPQTEEC_vendor",
		"libGPTEE_vendor",
		"libQTEEConnector_vendor",
	]

class DrmFirmwareSection(Section):
	name = "DRM firmware"
	folders = [
		"etc/firmware/drm",
	]
	patterns = [
		"(.*/)?firmware/widevine\..*",
	]

register_section(DrmSection)
register_section(DrmQseeSection)
register_section(DrmQteeSection)
register_section(DrmFirmwareSection)
