#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class GatekeeperSection(Section):
	name = "Gatekeeper"
	interfaces = [
		"android.hardware.gatekeeper",
		"vendor.microtrust.hardware.thh",
		"vendor.qti.hardware.secureprocessor",
		"vendor.qti.spu",
		"vendor.trustonic.tee",
	]
	binaries = [
		"teei_daemon",
	]
	hardware_modules = [
		"gatekeeper",
		"libSoftGatekeeper",
	]
	patterns = [
		"etc/init/microtrust.*\.rc",
	]
	properties_prefixes = {
		"vendor.gatekeeper.": False,
	}

class GatekeeperConfigsSection(Section):
	name = "Gatekeeper configs"
	folders = [
		"thh",
	]

register_section(GatekeeperSection)
register_section(GatekeeperConfigsSection)
