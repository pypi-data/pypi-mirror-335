#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class IpaSection(Section):
	name = "IPA"
	binaries = [
		"ipacm",
		"ipacm-diag",
	]
	libraries = [
		"libipanat",
		"liboffloadhal",
	]
	filenames = [
		"IPACM_cfg.xml",
	]

class IpaFirmwareSection(Section):
	name = "IPA firmware"
	filenames = [
		"ipa_fws.rc",
	]
	patterns = [
		"(.*/)?firmware/.*ipa_(fws|uc)*.",
	]

register_section(IpaSection)
register_section(IpaFirmwareSection)
