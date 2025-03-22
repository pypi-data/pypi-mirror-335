# -*- coding:utf-8 -*-
#
# Copyright (C) 2019-2020 Alibaba Group Holding Limited

from __future__ import print_function
from yoctools import *

import codecs
import shutil
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom

CDKSimulatorMachine = {
	# cpu: machine
	'e902': "soccfg/riscv32/smartl_e902_cfg.xml",
	'e902m': "soccfg/riscv32/smartl_e902_cfg.xml",
	'e902t': "soccfg/riscv32/smartl_e902_cfg.xml",
	'e902mt': "soccfg/riscv32/smartl_e902_cfg.xml",

	'e906': "soccfg/riscv32/smartl_e906_cfg.xml",
	'e906f': "soccfg/riscv32/smartl_e906_cfg.xml",
	'e906fd': "soccfg/riscv32/smartl_e906_cfg.xml",
	'e906p': "soccfg/riscv32/smartl_e906_cfg.xml",
	'e906fp': "soccfg/riscv32/smartl_e906_cfg.xml",
	'e906fdp': "soccfg/riscv32/smartl_e906_cfg.xml",

	'e907': "soccfg/riscv32/smartl_e907_cfg.xml",
	'e907f': "soccfg/riscv32/smartl_e907_cfg.xml",
	'e907fd': "soccfg/riscv32/smartl_e907_cfg.xml",
	'e907p': "soccfg/riscv32/smartl_e907_cfg.xml",
	'e907fp': "soccfg/riscv32/smartl_e907_cfg.xml",
	'e907fdp': "soccfg/riscv32/smartl_e907_cfg.xml",

	'c906': "soccfg/riscv64/xiaohui_c906_cfg.xml",
	'c906fd': "soccfg/riscv64/xiaohui_c906_cfg.xml",
	'c906fdv': "soccfg/riscv64/xiaohui_c906_cfg.xml",

	'c910': "soccfg/riscv64/xiaohui_c910_cfg.xml",
	'c920': "soccfg/riscv64/xiaohui_c920_cfg.xml",
	'r910': "soccfg/riscv64/xiaohui_r910_cfg.xml",
	'r920': "soccfg/riscv64/xiaohui_r920_cfg.xml",
	'r908': "soccfg/riscv64/xiaohui_r908_cfg.xml",
	'r908fd': "soccfg/riscv64/xiaohui_r908_cfg.xml",
	'r908fdv': "soccfg/riscv64/xiaohui_r908_cfg.xml",
	'r908-cp': "soccfg/riscv64/xiaohui_r908_cfg.xml",
	'r908fd-cp': "soccfg/riscv64/xiaohui_r908_cfg.xml",
	'r908fdv-cp': "soccfg/riscv64/xiaohui_r908_cfg.xml",

	'c908': "soccfg/riscv64/xiaohui_c908_cfg.xml",
	'c908i': "soccfg/riscv64/xiaohui_c908_cfg.xml",
	'c908v': "soccfg/riscv64/xiaohui_c908_cfg.xml",

	'c910v2': "soccfg/riscv64/xiaohui_c910v2_cfg.xml",
	'c910v3': "soccfg/riscv64/xiaohui_c910v3_cfg.xml",
	'c910v3-cp': "soccfg/riscv64/xiaohui_c910v3_cfg.xml",
	'c920v2': "soccfg/riscv64/xiaohui_c920v2_cfg.xml",
	'c920v3': "soccfg/riscv64/xiaohui_c920v3_cfg.xml",
	'c920v3-cp': "soccfg/riscv64/xiaohui_c920v3_cfg.xml",

	'c907': "soccfg/riscv64/xiaohui_c907_cfg.xml",
	'c907fd': "soccfg/riscv64/xiaohui_c907_cfg.xml",
	'c907fdv': "soccfg/riscv64/xiaohui_c907_cfg.xml",
	'c907fdvm': "soccfg/riscv64/xiaohui_c907_cfg.xml",
	'c907-rv32': "soccfg/riscv32/xiaohui_c907_cfg.xml",
	'c907fd-rv32': "soccfg/riscv32/xiaohui_c907_cfg.xml",
	'c907fdv-rv32': "soccfg/riscv32/xiaohui_c907_cfg.xml",
	'c907fdvm-rv32': "soccfg/riscv32/xiaohui_c907_cfg.xml",

	'c908x': "soccfg/riscv64/xiaohui_c908x_cfg.xml",
	'c908x-cp': "soccfg/riscv64/xiaohui_c908x_cfg.xml",
	'c908x-cp-xt': "soccfg/riscv64/xiaohui_c908x_cfg.xml",
}

def str_convert(text):
	if sys.version_info.major == 2:
		if type(text) == unicode:
			text = text.encode('utf8')
	if type(text) != str:
		text = str(text)
	return text

def defines_out(defines={}):
	text = ''
	if type(defines) == dict:
		for k, v in defines.items():
			if type(v) == str:
				text += '{}="{}";'.format(k, v)
			else:
				text += '{}={};'.format(k, v)
	return text

def indent(elem, level=0):
	i = "\n" + level * "  "
	if len(elem):
		if not elem.text or not elem.text.strip():
			elem.text = i + "  "
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
		for elem in elem:
			indent(elem, level + 1)
		if not elem.tail or not elem.tail.strip():
			elem.tail = i
	else:
		if level and (not elem.tail or not elem.tail.strip()):
			elem.tail = i

def create_xml_file_structure(path_depth, paths, root=None):
	if not len(paths):
		return None

	if not root:
		# Create the root element
		root_directory_name = os.path.normpath(paths[0]).split(os.sep)[path_depth]
		root = ET.Element("VirtualDirectory", Name=root_directory_name)

	# Helper function to recursively create XML elements
	def add_path_to_xml(parent, parts, path):
		if not parts:
			return

		part = parts.pop(0)
		existing_virtual_directory = None

		# Find if the VirtualDirectory or File already exists
		for child in parent:
			if child.tag == "VirtualDirectory" and child.attrib['Name'] == part:
				existing_virtual_directory = child
				break
			elif child.tag == "File" and child.attrib['Name'] == path:
				return

		if existing_virtual_directory is None:
			if parts:
				new_element = ET.SubElement(parent, "VirtualDirectory", Name=part)
				add_path_to_xml(new_element, parts, path)
			else:
				new_element = ET.SubElement(parent, "File", Name=path)
				ET.SubElement(new_element, "FileOption")
		else:
			add_path_to_xml(existing_virtual_directory, parts, path)

	# Process each path
	for path in paths:
		normalized_path = os.path.normpath(path)
		path_parts = normalized_path.split(os.sep)[path_depth + 1:]  # Remove the leading directory as it's already the root
		add_path_to_xml(root, path_parts, path)

	# indent(root)
	return root

class Cdkxml(Command):
	common = True
	helpSummary = "Generate current solution CDK XML project"
	helpUsage = """
%prog
"""
	helpDescription = """
generate current solution CDK XML project.
"""

	def _Options(self, p):
		p.add_option('-f', '--file',
					 dest='file', action='store', type='str', default=None,
					 help='the xt_rtos_sdk.csv file path')
		p.add_option('-s', '--solution',
							dest='solution', action='store', type='str', default=None,
							help='specify the solution name when use csv file to build cdk project. If there are multiple solutions, please separate them with commas')
		p.add_option('-p', '--platform',
							dest='platform', action='store', type='str', default=None,
							help='specify the platform when use csv file to build cdk project, If there are multiple platforms, please separate them with commas')
		p.add_option('-k', '--kernel',
							dest='kernel', action='store', type='str', default=None,
							help='specify the kernel when use csv file to build cdk project, If there are multiple kernels, please separate them with commas')
		p.add_option('-c', '--cpu',
					dest='cpu', action='store', type='str', default=None,
					help='specify the cpu when use csv file to build cdk project, If there are multiple cpus, please separate them with commas')
		p.add_option('-d', '--sdk',
					 dest='sdk_name', action='store', type='str', default=None,
					 help='specify chip sdk name, except dummy project.')
		p.add_option('-b', '--build_set',
					 dest='build_set', action='store', type='str', default=None,
					 help='specify the build set to generate.')

	def Execute(self, opt, args):
		cpu = platform = kernel = None
		if len(args) > 0:
			cpu = args[0]
		if len(args) > 1:
			platform = args[1]
		if len(args) > 2:
			kernel = args[2]

		global rv_cpus
		global platforms
		global kernels
		rv_cpus = globals()['RiscvCPU']
		platforms = globals()['xt_platforms']
		kernels = globals()['xt_kernels']

		def _build_cdk_proj(cpu, platform, kernel, solname=''):
			# print("cpu: %s, platform: %s, kernel: %s, solname: %s" % (cpu, platform, kernel, solname))
			if cpu:
				if not platform:
					put_string("Please input the platform argument.", level='warning')
					exit(1)
				put_string("Building [%s/%s/%s/%s] cdk project files, please wait..." % (solname, cpu, platform, kernel))
			elif opt.sdk_name:
				put_string("Building [%s] cdk project files, please wait..." % opt.sdk_name)
			else:
				put_string("Building cdk project files, please wait...")
			# put_string(os.getcwd())

			if cpu and (cpu not in rv_cpus):
				put_string("The cpu [%s] is not support yet!" % cpu, level='warning')
				put_string(rv_cpus)
				exit(1)
			if platform and (platform not in platforms):
				put_string("The platform [%s] is not support yet!" % platform, level='warning')
				put_string(platforms)
				exit(1)
			if kernel and (kernel not in kernels):
				put_string("The kernel [%s] is not support yet!" % kernel, level='warning')
				put_string(kernels)
				exit(1)

			if cpu:
				solution_packyaml = os.path.join(os.getcwd(), 'package.yaml')
				if not os.path.isfile(solution_packyaml):
					put_string("Can't find %s file." % solution_packyaml, level='warning')
					exit(1)
				is_have_sdkchip = False
				pack = Package(solution_packyaml)
				if pack.type != 'solution':
					put_string("The current directory is not a solution!!!", level='warning')
					exit(1)
				for d in pack.sdk_chip:
					if 'sdk_chip_wujian300' in d.keys() and platform == 'wujian300':
						is_have_sdkchip = True
						break
					if 'sdk_chip_riscv_dummy' in d.keys() and (platform == 'smartl' or platform == 'xiaohui'):
						is_have_sdkchip = True
						break
				if not is_have_sdkchip:
					for d in pack.depends:
						if 'sdk_chip_wujian300' in d.keys() and platform == 'wujian300':
							is_have_sdkchip = True
							break
						if 'sdk_chip_riscv_dummy' in d.keys() and (platform == 'smartl' or platform == 'xiaohui'):
							is_have_sdkchip = True
							break

				if platform == 'wujian300':
					chip_comp = os.path.join(os.getcwd(), '../../components/chip_wujian300')
					board_comp = os.path.join(os.getcwd(), '../../boards/board_wujian300_evb')
					sdkchip_comp = os.path.join(os.getcwd(), '../../components/sdk_chip_wujian300')
				else:
					chip_comp = os.path.join(os.getcwd(), '../../components/chip_riscv_dummy')
					board_comp = os.path.join(os.getcwd(), '../../boards/board_riscv_dummy')
					sdkchip_comp = os.path.join(os.getcwd(), '../../components/sdk_chip_riscv_dummy')

				chip_yaml_file = os.path.join(chip_comp, "package.yaml")
				chip_yaml_file_bak = os.path.join(chip_comp, "package.yaml" + ".bak")
				board_yaml_file = os.path.join(board_comp, "package.yaml")
				board_yaml_file_bak = os.path.join(board_comp, "package.yaml" + ".bak")
				sdkchip_yaml_file = os.path.join(sdkchip_comp, "package.yaml")
				sdkchip_yaml_file_bak = os.path.join(sdkchip_comp, "package.yaml" + ".bak")
				solution_yaml_file = os.path.join(os.getcwd(), "package.yaml")
				solution_yaml_file_bak = os.path.join(os.getcwd(), "package.yaml" + ".bak")
				build_chip_yaml_file = os.path.join(chip_comp, "package.yaml." + cpu)
				build_board_yaml_file = os.path.join(board_comp, "package.yaml." + platform)
				if not kernel:
					build_sdkchip_yaml_file = os.path.join(sdkchip_comp, "package.yaml." + 'bare')
					if solname.startswith('mcu_rtthread'):
						build_sdkchip_yaml_file = os.path.join(sdkchip_comp, "package.yaml." + 'rtthread')
					elif solname.startswith('mcu_freertos'):
						build_sdkchip_yaml_file = os.path.join(sdkchip_comp, "package.yaml." + 'freertos')
					else:
						pass
				else:
					build_sdkchip_yaml_file = os.path.join(sdkchip_comp, "package.yaml." + kernel)
				build_solution_yaml_file = os.path.join(os.getcwd(), "package.yaml." + cpu)
				build_solution_yaml_file2 = os.path.join(os.getcwd(), "package.yaml." + platform)

				if os.path.isfile(build_chip_yaml_file):
					shutil.copy2(chip_yaml_file, chip_yaml_file_bak)
					shutil.copy2(build_chip_yaml_file, chip_yaml_file)
				if os.path.isfile(build_board_yaml_file):
					shutil.copy2(board_yaml_file, board_yaml_file_bak)
					shutil.copy2(build_board_yaml_file, board_yaml_file)
				if os.path.isfile(build_sdkchip_yaml_file) and is_have_sdkchip:
					shutil.copy2(sdkchip_yaml_file, sdkchip_yaml_file_bak)
					shutil.copy2(build_sdkchip_yaml_file, sdkchip_yaml_file)
				if os.path.isfile(build_solution_yaml_file) or os.path.isfile(build_solution_yaml_file2):
					if os.path.isfile(build_solution_yaml_file):
						shutil.copy2(solution_yaml_file, solution_yaml_file_bak)
						shutil.copy2(build_solution_yaml_file, solution_yaml_file)
					else:
						shutil.copy2(solution_yaml_file, solution_yaml_file_bak)
						shutil.copy2(build_solution_yaml_file2, solution_yaml_file)

			def _clean_backup_file():
				if cpu:
					try:
						if os.path.isfile(chip_yaml_file_bak):
							shutil.copy2(chip_yaml_file_bak, chip_yaml_file)
							os.remove(chip_yaml_file_bak)
						if os.path.isfile(board_yaml_file_bak):
							shutil.copy2(board_yaml_file_bak, board_yaml_file)
							os.remove(board_yaml_file_bak)
						if os.path.isfile(sdkchip_yaml_file_bak):
							shutil.copy2(sdkchip_yaml_file_bak, sdkchip_yaml_file)
							os.remove(sdkchip_yaml_file_bak)
						if os.path.isfile(solution_yaml_file_bak):
							shutil.copy2(solution_yaml_file_bak, solution_yaml_file)
							os.remove(solution_yaml_file_bak)
					except Exception as ex:
						put_string(str(ex), level='warning')
						exit(1)

			yoc = YoC()
			solution = yoc.getSolution(sdk_name=opt.sdk_name, file_non_existent_no_err=True)
			if not solution:
				put_string("The current directory is not a solution!", level='warning')
				_clean_backup_file()
				exit(1)
			if opt.sdk_name:
				put_string(solution.board_component.name, solution.chip_component.name)

			if cpu and cpu != solution.cpu_name:
				put_string("The cpu name[%s,%s] is not match, please check!" % (cpu, solution.cpu_name), level='warning')
				_clean_backup_file()
				exit(1)

			cdk_proj_dir = os.path.join(os.getcwd(), 'cdk')
			if not os.path.exists(cdk_proj_dir):
				os.makedirs(cdk_proj_dir)
			cdk_proj_path_depth = 3
			# if opt.sdk_name:
			# 	cdk_proj_path_depth = cdk_proj_path_depth + 1
			# 	cdk_proj_dir = os.path.join(cdk_proj_dir, opt.sdk_name)
			if cpu:
				cdk_proj_path_depth = cdk_proj_path_depth + 1
				cdk_proj_dir = os.path.join(cdk_proj_dir, cpu)
			if platform:
				cdk_proj_path_depth = cdk_proj_path_depth + 1
				cdk_proj_dir = os.path.join(cdk_proj_dir, platform)
			if kernel:
				cdk_proj_path_depth = cdk_proj_path_depth + 1
				cdk_proj_dir = os.path.join(cdk_proj_dir, kernel)
			if not os.path.exists(cdk_proj_dir):
				os.makedirs(cdk_proj_dir)
			if not os.path.exists(cdk_proj_dir):
				put_string("The cdk dir %s is not exist, makedirs failed!" % cdk_proj_dir, level='warning')
				_clean_backup_file()
				exit(1)
			# print('cdk_proj_path_depth', cdk_proj_path_depth)
			# print("cdk_proj_dir: ", cdk_proj_dir)

			# print("solution.solution_component.name: ", solution.solution_component.name)
			mk = Make('cdkxml_proj_gen', sdkname = opt.sdk_name)
			mk.build_components()
			# print("mk.build_env.cds_cfgs:\n", mk.build_env.cds_cfgs)

			src_files = mk.build_env.cds_cfgs['cdk_src']
			inc_files = mk.build_env.cds_cfgs['cdk_inc_f']
			src_inc_files = mk.build_env.cds_cfgs['cdk_src_inc_f']
			includes = mk.build_env.cds_cfgs['CPPPATH']
			cppdefines = mk.build_env.cds_cfgs['CPPDEFINES']
			cflags_o = mk.build_env.cds_cfgs['CFLAGS']
			cxxflags_o = mk.build_env.cds_cfgs['CXXFLAGS']
			asflags_o = mk.build_env.cds_cfgs['ASFLAGS']
			linkflags_o = mk.build_env.cds_cfgs['LINKFLAGS']

			# remove -mcpu
			cflags = []
			for e in cflags_o:
				if not e.startswith("-mcpu="):
					cflags.append(e)
			cxxflags = []
			for e in cxxflags_o:
				if not e.startswith("-mcpu="):
					cxxflags.append(e)
			asflags = []
			for e in asflags_o:
				if not e.startswith("-mcpu="):
					asflags.append(e)
			linkflags = []
			for e in linkflags_o:
				if not e.startswith("-mcpu="):
					linkflags.append(e)

			###################################################
			yoc_base_path = yoc.yoc_path
			sbc_base_path = ''
			for i in range(0, cdk_proj_path_depth):
				sbc_base_path = sbc_base_path + "../"

			virtual_dir_txt = ''
			xml_root2 = None
			comp_paths = []
			for k, v in src_inc_files.items():
				if k.type == 'solution':
					paths = []
					for f in v:
						file_path = sbc_base_path + os.path.relpath(f, yoc_base_path)
						paths.append(file_path)
					xml_root = create_xml_file_structure(cdk_proj_path_depth, paths)
					if xml_root:
						xml_txt = ET.tostring(xml_root, encoding='utf-8', method='xml').decode()
						virtual_dir_txt += xml_txt
				elif k.type == 'board':
					paths = []
					for f in v:
						file_path = sbc_base_path + os.path.relpath(f, yoc_base_path)
						paths.append(file_path)
					xml_root = create_xml_file_structure(cdk_proj_path_depth, paths)
					if xml_root:
						xml_txt = ET.tostring(xml_root, encoding='utf-8', method='xml').decode()
						virtual_dir_txt += xml_txt
				else:
					for f in v:
						file_path = sbc_base_path + os.path.relpath(f, yoc_base_path)
						comp_paths.append(file_path)

			xml_root2 = create_xml_file_structure(cdk_proj_path_depth, comp_paths)
			xml_txt2 = ''
			if xml_root2:
				xml_txt2 = ET.tostring(xml_root2, encoding='utf-8', method='xml').decode()
			virtual_dir_txt += xml_txt2
			# print(virtual_dir_txt)

			# libs path
			libpath_txts = ''
			for l in solution.external_libpath:
				l = sbc_base_path + os.path.relpath(l, yoc_base_path)
				libpath_txts += ''.join("%s;" % l)
			# print("libpath_txts:", libpath_txts)

			# libs
			# print("external_libs:", solution.external_libs)
			exlibs = solution.external_libs
			if 'm' not in exlibs:
				exlibs.append('m')
			libs_txts = ''
			for l in exlibs:
				libs_txts += ''.join("%s;" % l)
			# print("libs_txts:", libs_txts)

			otherflags = []
			othercppflags = []
			for f in cflags:
				if f not in otherflags:
					otherflags.append(f)
			# print("otherflags:", otherflags)
			for f in cxxflags:
				# if f not in othercppflags:
					# othercppflags.append(f)
				if f not in otherflags:
					otherflags.append(f)
			# print("2otherflags:", otherflags)

			includes_ctx = ''
			for f in includes:
				f = sbc_base_path + os.path.relpath(f, yoc_base_path)
				includes_ctx += ''.join("%s;" % f)
			# print(includes_ctx)

			sol_relpath = sbc_base_path + os.path.relpath(solution.solution_component.path, yoc_base_path)
			board_relpath = sbc_base_path + os.path.relpath(solution.board_component.path, yoc_base_path)
			chip_relpath = sbc_base_path + os.path.relpath(solution.chip_component.path, yoc_base_path)
			before_make_script = sbc_base_path + os.path.relpath("./script/before_build.sh", yoc_base_path)
			before_make_script += " " + sol_relpath
			before_make_script += " " + board_relpath
			before_make_script += " " + chip_relpath
			before_make_script += " " + platform
			before_make_script += " " + cpu
			before_make_script += " " + '$(OBJCOPY) $(OBJDUMP)'

			after_make_script = sbc_base_path + os.path.relpath("./script/after_build.sh", yoc_base_path)
			after_make_script += " " + sol_relpath
			after_make_script += " " + board_relpath
			after_make_script += " " + chip_relpath
			after_make_script += " " + platform
			after_make_script += " " + cpu
			after_make_script += " " + '$(OBJCOPY) $(OBJDUMP)'

			if kernel:
				proj_name = "%s_%s_%s_%s" % (solution.solution_component.name, cpu, platform, kernel)
			else:
				proj_name = "%s_%s_%s" % (solution.solution_component.name, cpu, platform)

			smp_cpu_flags = "-smp cpus=4"
			if cpu.startswith('e') or cpu.startswith('c906'):
				smp_cpu_flags = ''
			ccflags_llvm = ' '.join(otherflags)
			if solution.solution_component.name == 'bare_coremark':
				gccflags = '-O3 -funroll-all-loops -finline-limit=500 -fgcse-sm -msignedness-cmpiv -fno-code-hoisting -mno-thread-jumps1 -mno-iv-adjust-addr-cost -mno-expand-split-imm -fselective-scheduling -fgcse-las'
				llvmflags = '-O3 -mllvm -inline-threshold=500 -mllvm -riscv-default-unroll=false -mllvm -jump-threading-threshold=0 -mllvm -enable-dfa-jump-thread=true -Wno-macro-redefined'
				ccflags_llvm = ccflags_llvm.replace(gccflags, llvmflags)
				# print(ccflags_llvm)

			cproject_content = cproject_template.format(
				name = proj_name ,
				description = str_convert(solution.solution_component.description),
				virtual_directory_ctx = virtual_dir_txt,
				cpu_name = solution.cpu_name,
				before_make_script = before_make_script,
				after_make_script = after_make_script,
				defines = defines_out(solution.defines),
				includes_path = includes_ctx,
				CCFLAGS = ' '.join(otherflags),
				CCFLAGS_LLV = ccflags_llvm,
				ASMFLAGS = ' '.join(asflags),
				ld_script = sbc_base_path + os.path.relpath(solution.ld_script, yoc_base_path),
				libs_name = libs_txts,
				libs_path = libpath_txts,
				LINKFLAGS = ' '.join(linkflags),
				simulator_machine = CDKSimulatorMachine[cpu],
				sim_otherflags = smp_cpu_flags,
				# algorithms_path = sbc_base_path + os.path.relpath(solution.algorithms_path, yoc_base_path)
			)
			# prj_root = ET.fromstring(cproject_content)
			# indent(prj_root)
			# cproject_content = ET.tostring(prj_root, encoding='utf-8', method='xml').decode()
			# print(cproject_content)
			def __remove_node(parse_xml, target_name):
				root = parse_xml.documentElement
				build_configs = root.getElementsByTagName("BuildConfig")
				target_node = None
				for node in build_configs:
					if node.getAttribute("Name") == target_name:
						target_node = node
						break
				if target_node:
					parent = target_node.parentNode
					parent.removeChild(target_node)
				return parse_xml

			parse_xml = minidom.parseString(cproject_content)
			if opt.build_set == "llvm":
				parse_xml = __remove_node(parse_xml, "BuildSet_GCC")
			elif opt.build_set == "gcc":
				parse_xml = __remove_node(parse_xml, "BuildSet_LLVM")

			cproject_content = parse_xml.toprettyxml(indent="  ")
			cproject_content = '\n'.join(line for line in cproject_content.split('\n') if line.strip() != '')
			cproject_content += '\n'
			# print(cproject_content)

			# generate cdk project files
			try:
				filename = os.path.join(solution.solution_component.path, os.path.join(cdk_proj_dir, 'project.cdkproj'))
				with codecs.open(filename, 'w', 'UTF-8') as f:
					if sys.version_info.major == 2:
						if type(cproject_content) == str:
							cproject_content = cproject_content.decode('UTF-8')
					f.write(cproject_content)
					put_string("Generate project.cdkproj file success.", level='info')
			except Exception as ex:
				put_string("Generate %s file failed." % filename, level='warning')
				put_string(str(ex))
				_clean_backup_file()
				exit(1)

			try:
				global gitignore_txt
				filename = os.path.join(solution.solution_component.path, os.path.join(cdk_proj_dir, '.gitignore'))
				with codecs.open(filename, 'w', 'UTF-8') as f:
					if sys.version_info.major == 2:
						if type(gitignore_txt) == str:
							gitignore_txt = gitignore_txt.decode('UTF-8')
					f.write(gitignore_txt)
					put_string("Generate cdk .gitignore file success.", level='info')
			except Exception as ex:
				put_string("Generate %s file failed.(%s)" % (filename, str(ex)), level='warning')
				_clean_backup_file()
				exit(1)

			_clean_backup_file()
			put_string("Generate cdk project at [%s] success." % cdk_proj_dir, level='info')
		###################################################

		if opt.file:
			csv_file = os.path.realpath(opt.file)
			if not os.path.isfile(csv_file):
				put_string("Please check the file %s is exists." % csv_file, level='warning')
				exit(1)
			put_string("Use %s file to build all cdk projects." % csv_file)
			yoc = YoC()
			specify_solution_list = []
			specify_platform_list = []
			specify_kernel_list = []
			specify_cpu_list = []
			if opt.solution:
				specify_solution_list = opt.solution.split(",")
				put_string("specify_solution_list: ", specify_solution_list)
			else:
				solution = yoc.getSolution()
				if solution:
					specify_solution_list.append(solution.solution_component.name)
			if opt.platform:
				specify_platform_list = opt.platform.split(',')
				put_string("specify_platform_list: ", specify_platform_list)
			if opt.kernel:
				specify_kernel_list = opt.kernel.split(',')
				put_string("specify_kernel_list: ", specify_kernel_list)
			if opt.cpu:
				specify_cpu_list = opt.cpu.split(',')
				put_string("specify_cpu_list: ", specify_cpu_list)
			try:
				with codecs.open(csv_file, 'r', 'UTF-8') as f:
					csvreader = csv.reader(f)
					cnt = 0
					for row in csvreader:
						if len(row) == 0:
							continue
						#skip first line
						if cnt != 0:
							sname = row[0].strip()
							cpu_list = [word.strip() for word in row[1].split('/')]
							cdk_Y_N = row[3].strip()
							# print('cdk_Y_N: ', cdk_Y_N)
							# print(sname, specify_solution_list)
							if len(specify_solution_list) > 0 and (sname not in specify_solution_list):
								continue
							if cdk_Y_N == 'N':
								put_string("No need to build cdk for %s." % sname, color='blue')
								continue

							def _build_with_csv():
								sol = os.path.join(yoc.yoc_path, "solutions", sname)
								if not os.path.exists(sol):
									put_string("%s not found, please check." % sol, level='warning')
									return
								os.chdir(sol)
								for c in cpu_list:
									cpu = c
									if opt.cpu and (cpu not in specify_cpu_list):
										continue
									if len(specify_platform_list) > 0:
										for p in specify_platform_list:
											try:
												_build_cdk_proj(cpu, p, kernel, sname)
											except Exception as ex:
												put_string(str(ex), level='warning')
												exit(1)
									else:
										platform = 'xiaohui'
										if c.startswith("e"):
											platform = 'smartl'
										# print(sname, cpu, platform, kernel)
										try:
											_build_cdk_proj(cpu, platform, kernel, sname)
										except Exception as ex:
											put_string(str(ex), level='warning')
											exit(1)

							if sname != 'solutions':
								if sname.startswith('soc_'):
									# soc_xx demo support multi type kernel
									for k in kernels:
										kernel = k
										if len(specify_kernel_list) > 0 and (kernel not in specify_kernel_list):
											continue
										_build_with_csv()
								else:
									kernel = None
									_build_with_csv()
						cnt += 1
				exit(1)
			except Exception as ex:
				put_string("Read %s file failed.(%s)" % (csv_file, str(ex)), level='warning')
				exit(1)

		try:
			yoc = YoC()
			solution = yoc.getSolution()
			_build_cdk_proj(cpu, platform, kernel, solution.solution_component.name)
		except Exception as ex:
			put_string(str(ex), level='warning')
			exit(1)

gitignore_txt = '''
/Debug/
/Release/
/boards/
/components/
/solutions/
cdkws.mk
Obj/
Lst/
__workspace_pack__/
.cdk
.cache
*.cdkws
*.mk
*.bat
'''

cproject_template = """<?xml version="1.0" encoding="UTF-8"?>
<Project Name="{name}" Version="1" Language="C">
  <Description>{description}</Description>
  <Dependencies Name="Debug"/>
  {virtual_directory_ctx}
  <VendorInfo>
    <VendorName>import_sdk_project</VendorName>
  </VendorInfo>
  <ToolsConfig>
    <Compiler>
      <Name>XTGccElfNewlib</Name>
      <Version>latest</Version>
    </Compiler>
  </ToolsConfig>
  <DebugSessions>
    <watchExpressions/>
    <memoryExpressions>;;;</memoryExpressions>
    <statistics>;;MHZ</statistics>
    <peripheralTabs/>
    <WatchDisplayFormat/>
    <LocalDisplayFormat/>
    <debugLayout/>
    <memoryTabColSizeExpressions/>
    <QuickWatchDisplayFormat/>
  </DebugSessions>
  <BuildConfigs>
	<BuildConfig Name="BuildSet_GCC">
	  <Target>
		<ROMBank Selected="1">
		  <ROM1>
			<InUse>no</InUse>
			<Start/>
			<Size/>
		  </ROM1>
		  <ROM2>
			<InUse>no</InUse>
			<Start/>
			<Size/>
		  </ROM2>
		  <ROM3>
			<InUse>no</InUse>
			<Start/>
			<Size/>
		  </ROM3>
		  <ROM4>
			<InUse>no</InUse>
			<Start/>
			<Size/>
		  </ROM4>
		  <ROM5>
			<InUse>no</InUse>
			<Start/>
			<Size/>
		  </ROM5>
		</ROMBank>
		<RAMBank>
		  <RAM1>
			<InUse>no</InUse>
			<Start/>
			<Size/>
			<Init>yes</Init>
		  </RAM1>
		  <RAM2>
			<InUse>no</InUse>
			<Start/>
			<Size/>
			<Init>yes</Init>
		  </RAM2>
		  <RAM3>
			<InUse>no</InUse>
			<Start/>
			<Size/>
			<Init>yes</Init>
		  </RAM3>
		  <RAM4>
			<InUse>no</InUse>
			<Start/>
			<Size/>
			<Init>yes</Init>
		  </RAM4>
		  <RAM5>
			<InUse>no</InUse>
			<Start/>
			<Size/>
			<Init>yes</Init>
		  </RAM5>
		</RAMBank>
		<CPU>{cpu_name}</CPU>
		<UseMiniLib>yes</UseMiniLib>
		<Endian>little</Endian>
		<UseEnhancedLRW>no</UseEnhancedLRW>
		<UseContinueBuild>no</UseContinueBuild>
		<ToolchainID>XTGccElfNewlib</ToolchainID>
		<ToolchainVersion>latest</ToolchainVersion>
		<UseSemiHost>no</UseSemiHost>
	  </Target>
	  <Output>
		<OutputName>$(ProjectName)</OutputName>
		<Type>Executable</Type>
		<CreateHexFile>no</CreateHexFile>
		<CreateBinFile>no</CreateBinFile>
		<Preprocessor>no</Preprocessor>
		<Disassmeble>no</Disassmeble>
		<CallGraph>no</CallGraph>
		<Map>no</Map>
	  </Output>
	  <User>
		<BeforeCompile>
		  <RunUserProg>no</RunUserProg>
		  <UserProgName/>
		  <IsBatchScript>no</IsBatchScript>
		</BeforeCompile>
		<BeforeMake>
		  <RunUserProg>yes</RunUserProg>
		  <UserProgName>{before_make_script}</UserProgName>
		  <IsBatchScript>no</IsBatchScript>
		</BeforeMake>
		<AfterMake>
		  <RunUserProg>yes</RunUserProg>
		  <UserProgName>{after_make_script}</UserProgName>
		  <IsBatchScript>no</IsBatchScript>
		</AfterMake>
		<Tools/>
	  </User>
	  <Compiler>
		<Define>{defines}</Define>
		<Undefine/>
		<Optim>Default</Optim>
		<DebugLevel>Default (-g)</DebugLevel>
		<IncludePath>$(ProjectPath);{includes_path}</IncludePath>
		<OtherFlags>{CCFLAGS}</OtherFlags>
		<Verbose>no</Verbose>
		<Ansi>no</Ansi>
		<Syntax>no</Syntax>
		<Pedantic>no</Pedantic>
		<PedanticErr>no</PedanticErr>
		<InhibitWarn>no</InhibitWarn>
		<AllWarn>yes</AllWarn>
		<WarnErr>no</WarnErr>
		<OneElfS>no</OneElfS>
		<OneElfSPerData>no</OneElfSPerData>
		<Fstrict>no</Fstrict>
	  </Compiler>
	  <Asm>
		<Define>{defines}</Define>
		<Undefine/>
		<IncludePath>$(ProjectPath);{includes_path}</IncludePath>
		<OtherFlags>{ASMFLAGS}</OtherFlags>
		<DebugLevel>none</DebugLevel>
	  </Asm>
	  <Linker>
		<Garbage>yes</Garbage>
		<Garbage2>yes</Garbage2>
		<LDFile>{ld_script}</LDFile>
		<LibName>{libs_name}</LibName>
		<LibPath>{libs_path}</LibPath>
		<OtherFlags>{LINKFLAGS}</OtherFlags>
		<AutoLDFile>no</AutoLDFile>
		<LinkType>whole-archive</LinkType>
		<IncludeAllLibs>yes</IncludeAllLibs>
		<LinkSpecsType>none</LinkSpecsType>
		<LinkUseNewlibNano>no</LinkUseNewlibNano>
	  </Linker>
	  <Debug>
		<LoadApplicationAtStartup>yes</LoadApplicationAtStartup>
		<Connector>SIM</Connector>
		<StopAt>yes</StopAt>
		<StopAtText>main</StopAtText>
		<InitFile>$(ProjectPath)/gdbinit.remote</InitFile>
		<PreInit/>
		<AfterLoadFile/>
		<AutoRun>yes</AutoRun>
		<ResetType>Hard Reset</ResetType>
		<SoftResetVal>0</SoftResetVal>
		<ResetAfterLoad>no</ResetAfterLoad>
		<AfterResetFile/>
		<Dumpcore>no</Dumpcore>
		<DumpcoreText/>
		<SVCFile/>
		<ConfigICE>
		  <IP>localhost</IP>
		  <PORT>1025</PORT>
		  <CPUNumber>0</CPUNumber>
		  <Clock>12000</Clock>
		  <Delay>10</Delay>
		  <NResetDelay>100</NResetDelay>
		  <WaitReset>50</WaitReset>
		  <DDC>yes</DDC>
		  <TRST>no</TRST>
		  <PreReset>no</PreReset>
		  <DebugPrint>no</DebugPrint>
		  <Connect>Normal</Connect>
		  <ResetType>soft</ResetType>
		  <SoftResetVal>0</SoftResetVal>
		  <RTOSType>None</RTOSType>
		  <DownloadToFlash>no</DownloadToFlash>
		  <ResetAfterConnect>yes</ResetAfterConnect>
		  <GDBName/>
		  <GDBServerType>Local</GDBServerType>
		  <OtherFlags/>
		  <ICEEnablePCSampling>no</ICEEnablePCSampling>
		  <ICESamplingFreq>1000</ICESamplingFreq>
		  <RemoteICEEnablePCSampling>no</RemoteICEEnablePCSampling>
		  <RemoteICESamplingPort>1026</RemoteICESamplingPort>
		  <Version>latest</Version>
		  <SupportRemoteICEAsyncDebug>no</SupportRemoteICEAsyncDebug>
		</ConfigICE>
		<ConfigSIM>
		  <SIMTarget>{simulator_machine}</SIMTarget>
		  <OtherFlags>{sim_otherflags}</OtherFlags>
		  <NoGraphic>yes</NoGraphic>
		  <Log>no</Log>
		  <SimTrace>no</SimTrace>
		  <Version>latest</Version>
		</ConfigSIM>
		<ConfigOpenOCD>
		  <OpenOCDExecutablePath/>
		  <OpenOCDLocally>yes</OpenOCDLocally>
		  <OpenOCDTelnetPortEnable>no</OpenOCDTelnetPortEnable>
		  <OpenOCDTelnetPort>4444</OpenOCDTelnetPort>
		  <OpenOCDTclPortEnable>no</OpenOCDTclPortEnable>
		  <OpenOCDTclPort>6666</OpenOCDTclPort>
		  <OpenOCDConfigOptions/>
		  <OpenOCDTimeout>5000</OpenOCDTimeout>
		  <OpenOCDRemoteIP>localhost</OpenOCDRemoteIP>
		  <OpenOCDRemotePort>3333</OpenOCDRemotePort>
		  <PluginID>openocd-sifive</PluginID>
		  <Version>latest</Version>
		</ConfigOpenOCD>
	  </Debug>
	  <Flash>
		<InitFile></InitFile>
		<PreInit/>
		<Erase>Erase Sectors</Erase>
		<Algorithms Path=""></Algorithms>
		<Program>no</Program>
		<Verify>no</Verify>
		<ResetAndRun>no</ResetAndRun>
		<ResetType/>
		<SoftResetVal/>
		<FlashIndex>no</FlashIndex>
		<FlashIndexVal>0</FlashIndexVal>
		<External>no</External>
		<Command/>
		<Arguments/>
	  </Flash>
	</BuildConfig>
	<BuildConfig Name="BuildSet_LLVM">
	  <Target>
		<ROMBank Selected="1">
		  <ROM1>
			<InUse>no</InUse>
			<Start/>
			<Size/>
		  </ROM1>
		  <ROM2>
			<InUse>no</InUse>
			<Start/>
			<Size/>
		  </ROM2>
		  <ROM3>
			<InUse>no</InUse>
			<Start/>
			<Size/>
		  </ROM3>
		  <ROM4>
			<InUse>no</InUse>
			<Start/>
			<Size/>
		  </ROM4>
		  <ROM5>
			<InUse>no</InUse>
			<Start/>
			<Size/>
		  </ROM5>
		</ROMBank>
		<RAMBank>
		  <RAM1>
			<InUse>no</InUse>
			<Start/>
			<Size/>
			<Init>yes</Init>
		  </RAM1>
		  <RAM2>
			<InUse>no</InUse>
			<Start/>
			<Size/>
			<Init>yes</Init>
		  </RAM2>
		  <RAM3>
			<InUse>no</InUse>
			<Start/>
			<Size/>
			<Init>yes</Init>
		  </RAM3>
		  <RAM4>
			<InUse>no</InUse>
			<Start/>
			<Size/>
			<Init>yes</Init>
		  </RAM4>
		  <RAM5>
			<InUse>no</InUse>
			<Start/>
			<Size/>
			<Init>yes</Init>
		  </RAM5>
		</RAMBank>
		<CPU>{cpu_name}</CPU>
		<UseMiniLib>yes</UseMiniLib>
		<Endian>little</Endian>
		<UseEnhancedLRW>no</UseEnhancedLRW>
		<UseContinueBuild>no</UseContinueBuild>
		<ToolchainID>XTLLVMElfNewlib</ToolchainID>
		<ToolchainVersion>latest</ToolchainVersion>
		<UseSemiHost>no</UseSemiHost>
	  </Target>
	  <Output>
		<OutputName>$(ProjectName)</OutputName>
		<Type>Executable</Type>
		<CreateHexFile>no</CreateHexFile>
		<CreateBinFile>no</CreateBinFile>
		<Preprocessor>no</Preprocessor>
		<Disassmeble>no</Disassmeble>
		<CallGraph>no</CallGraph>
		<Map>no</Map>
	  </Output>
	  <User>
		<BeforeCompile>
		  <RunUserProg>no</RunUserProg>
		  <UserProgName/>
		  <IsBatchScript>no</IsBatchScript>
		</BeforeCompile>
		<BeforeMake>
		  <RunUserProg>yes</RunUserProg>
		  <UserProgName>{before_make_script}</UserProgName>
		  <IsBatchScript>no</IsBatchScript>
		</BeforeMake>
		<AfterMake>
		  <RunUserProg>yes</RunUserProg>
		  <UserProgName>{after_make_script}</UserProgName>
		  <IsBatchScript>no</IsBatchScript>
		</AfterMake>
		<Tools/>
	  </User>
	  <Compiler>
		<Define>{defines}</Define>
		<Undefine/>
		<Optim>Default</Optim>
		<DebugLevel>Default (-g)</DebugLevel>
		<IncludePath>$(ProjectPath);{includes_path}</IncludePath>
		<OtherFlags>{CCFLAGS_LLV}</OtherFlags>
		<Verbose>no</Verbose>
		<Ansi>no</Ansi>
		<Syntax>no</Syntax>
		<Pedantic>no</Pedantic>
		<PedanticErr>no</PedanticErr>
		<InhibitWarn>no</InhibitWarn>
		<AllWarn>yes</AllWarn>
		<WarnErr>no</WarnErr>
		<OneElfS>no</OneElfS>
		<OneElfSPerData>no</OneElfSPerData>
		<Fstrict>no</Fstrict>
	  </Compiler>
	  <Asm>
		<Define>{defines}</Define>
		<Undefine/>
		<IncludePath>$(ProjectPath);{includes_path}</IncludePath>
		<OtherFlags>{ASMFLAGS}</OtherFlags>
		<DebugLevel>none</DebugLevel>
	  </Asm>
	  <Linker>
		<Garbage>yes</Garbage>
		<Garbage2>yes</Garbage2>
		<LDFile>{ld_script}</LDFile>
		<LibName>{libs_name}</LibName>
		<LibPath>{libs_path}</LibPath>
		<OtherFlags>{LINKFLAGS}</OtherFlags>
		<AutoLDFile>no</AutoLDFile>
		<LinkType>whole-archive</LinkType>
		<IncludeAllLibs>yes</IncludeAllLibs>
		<LinkSpecsType>none</LinkSpecsType>
		<LinkUseNewlibNano>no</LinkUseNewlibNano>
	  </Linker>
	  <Debug>
		<LoadApplicationAtStartup>yes</LoadApplicationAtStartup>
		<Connector>SIM</Connector>
		<StopAt>yes</StopAt>
		<StopAtText>main</StopAtText>
		<InitFile>$(ProjectPath)/gdbinit.remote</InitFile>
		<PreInit/>
		<AfterLoadFile/>
		<AutoRun>yes</AutoRun>
		<ResetType>Hard Reset</ResetType>
		<SoftResetVal>0</SoftResetVal>
		<ResetAfterLoad>no</ResetAfterLoad>
		<AfterResetFile/>
		<Dumpcore>no</Dumpcore>
		<DumpcoreText/>
		<SVCFile/>
		<ConfigICE>
		  <IP>localhost</IP>
		  <PORT>1025</PORT>
		  <CPUNumber>0</CPUNumber>
		  <Clock>12000</Clock>
		  <Delay>10</Delay>
		  <NResetDelay>100</NResetDelay>
		  <WaitReset>50</WaitReset>
		  <DDC>yes</DDC>
		  <TRST>no</TRST>
		  <PreReset>no</PreReset>
		  <DebugPrint>no</DebugPrint>
		  <Connect>Normal</Connect>
		  <ResetType>soft</ResetType>
		  <SoftResetVal>0</SoftResetVal>
		  <RTOSType>None</RTOSType>
		  <DownloadToFlash>no</DownloadToFlash>
		  <ResetAfterConnect>yes</ResetAfterConnect>
		  <GDBName/>
		  <GDBServerType>Local</GDBServerType>
		  <OtherFlags/>
		  <ICEEnablePCSampling>no</ICEEnablePCSampling>
		  <ICESamplingFreq>1000</ICESamplingFreq>
		  <RemoteICEEnablePCSampling>no</RemoteICEEnablePCSampling>
		  <RemoteICESamplingPort>1026</RemoteICESamplingPort>
		  <Version>latest</Version>
		  <SupportRemoteICEAsyncDebug>no</SupportRemoteICEAsyncDebug>
		</ConfigICE>
		<ConfigSIM>
		  <SIMTarget>{simulator_machine}</SIMTarget>
		  <OtherFlags>{sim_otherflags}</OtherFlags>
		  <NoGraphic>yes</NoGraphic>
		  <Log>no</Log>
		  <SimTrace>no</SimTrace>
		  <Version>latest</Version>
		</ConfigSIM>
		<ConfigOpenOCD>
		  <OpenOCDExecutablePath/>
		  <OpenOCDLocally>yes</OpenOCDLocally>
		  <OpenOCDTelnetPortEnable>no</OpenOCDTelnetPortEnable>
		  <OpenOCDTelnetPort>4444</OpenOCDTelnetPort>
		  <OpenOCDTclPortEnable>no</OpenOCDTclPortEnable>
		  <OpenOCDTclPort>6666</OpenOCDTclPort>
		  <OpenOCDConfigOptions/>
		  <OpenOCDTimeout>5000</OpenOCDTimeout>
		  <OpenOCDRemoteIP>localhost</OpenOCDRemoteIP>
		  <OpenOCDRemotePort>3333</OpenOCDRemotePort>
		  <PluginID>openocd-sifive</PluginID>
		  <Version>latest</Version>
		</ConfigOpenOCD>
	  </Debug>
	  <Flash>
		<InitFile></InitFile>
		<PreInit/>
		<Erase>Erase Sectors</Erase>
		<Algorithms Path=""></Algorithms>
		<Program>no</Program>
		<Verify>no</Verify>
		<ResetAndRun>no</ResetAndRun>
		<ResetType/>
		<SoftResetVal/>
		<FlashIndex>no</FlashIndex>
		<FlashIndexVal>0</FlashIndexVal>
		<External>no</External>
		<Command/>
		<Arguments/>
	  </Flash>
	</BuildConfig>
  </BuildConfigs>
</Project>
"""
