#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class WifiDisplaySection(Section):
	name = "Wi-Fi Display"
	interfaces = [
		"com.qualcomm.qti.wifidisplayhal",
		"vendor.qti.hardware.sigma_miracast",
		"vendor.qti.hardware.wifidisplaysession",
	]
	apps = [
		"WfdService",
	]
	binaries = [
		"wfdhdcphalservice",
		"wfdservice",
		"wfdvndservice",
		"wifidisplayhalservice",
	]
	libraries = [
		"libmiracast",
	]
	filenames = [
		"wfdconfig.xml",
		"wifidisplayhalservice.policy",
	]
	patterns = [
		"etc/seccomp_policy/wfd.*.service\.policy",
	]
	properties_prefixes = {
		"persist.debug.wfd.": False,
		"persist.sys.wfd.": False,
	}

register_section(WifiDisplaySection)
