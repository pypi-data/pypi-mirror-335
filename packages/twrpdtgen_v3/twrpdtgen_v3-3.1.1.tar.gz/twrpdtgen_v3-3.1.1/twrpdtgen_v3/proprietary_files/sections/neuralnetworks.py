#
#
# Copyright (C) 2025 The LineageOS Project
# Copyright (C) 2025 xXHenneBXx
# SPDX-License-Identifier: Apache-2.0
#

from twrpdtgen_v3.proprietary_files.section import Section, register_section

class NeuralNetworksSection(Section):
	name = "Neural networks"
	interfaces = [
		"android.hardware.neuralnetworks",
		"vendor.mediatek.hardware.mmagent",
	]
	binaries = [
		"nn_device_test",
		"npu_launcher",
	]
	libraries = [
		"libhexagon_nn_stub",
	]
	patterns = [
		"lib(64)?/libhta(_.*.)?\.so",
		"lib(64)?/unnhal.*.\.so",
	]

register_section(NeuralNetworksSection)
