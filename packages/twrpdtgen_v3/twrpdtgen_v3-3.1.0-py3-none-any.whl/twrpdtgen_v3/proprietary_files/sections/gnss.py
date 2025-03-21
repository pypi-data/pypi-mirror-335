#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class GnssSection(Section):
	name = "GNSS"
	interfaces = [
		"android.hardware.gnss",
		"android.hardware.gnss.measurement_corrections",
		"android.hardware.gnss.visibility_control",
		"vendor.qti.gnss",
	]
	hardware_modules = [
		"gps",
	]
	binaries = [
		"loc_launcher",
		"lowi-server",
		"mnld",
		"mtk_agpsd",
		"slim_daemon",
		"xtra-daemon",
		"xtwifi-client",
		"xtwifi-inet-agent",
	]
	patterns = [
		"etc/init/mtk_agps.*\.rc",
	]
	properties_prefixes = {
		"persist.sys.gps.": False,
		"persist.vendor.overlay.izat.": False,
	}

class GnssConfigsSection(Section):
	name = "GNSS configs"
	filenames = [
		"apdr.conf",
		"flp.conf",
		"gps.conf",
		"izat.conf",
		"lowi.conf",
		"sap.conf",
		"xtwifi.conf",
	]
	folders = [
		"etc/gnss",
	]

register_section(GnssSection)
register_section(GnssConfigsSection)
