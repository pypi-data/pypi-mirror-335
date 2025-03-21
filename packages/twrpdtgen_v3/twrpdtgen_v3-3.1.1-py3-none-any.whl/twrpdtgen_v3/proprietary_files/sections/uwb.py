#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class UwbSection(Section):
    name = "UWB"
    interfaces = [
        "android.hardware.uwb",
        "android.hardware.uwb.fira_android",
    ]

register_section(UwbSection)
