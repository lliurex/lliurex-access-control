#!/usr/bin/python3

import os
import subprocess
import json
import codecs
import configparser

import n4d.responses
import n4d.server.core as n4dcore

class AccessControlManager:

	DISABLE_GROUP_ACCESS_CONTROL_ERROR=-10
	SET_GROUP_ERROR=-20
	DISABLE_USER_ACCESS_CONTROL_ERROR=-30
	SET_USER_ERROR=-40
	DISABLE_CDC_ACCESS_CONTROL_ERROR=-50
	SET_CDC_ERROR=-60

	def __init__(self):

		self.core=n4dcore.Core.get_core()
		self.config_path="/etc/lliurex-access-control"
		self.data_path="/usr/share/lliurex-access-control-config/GroupsLists"
		self.group_template_path=os.path.join(self.data_path,"defaultGroups.json")
		self.group_deny_list_path=os.path.join(self.config_path,"login.group.deny")
		self.default_groups_file=os.path.join(self.config_path+"/groups-lists","defaultGroups.json")
		self.user_denied_list_path=os.path.join(self.config_path,"login.user.deny")
		self.users_list=os.path.join(self.config_path+"/users-lists","usersList.json")
		self.sssd_config_path="/etc/sssd/sssd.conf"
		self.cdc_info=os.path.join(self.config_path+"/cdc-info","cdc.json")
		self.section_ref_desa="domain/DESEDU.GVA.ES"
		self.section_ref_pro="domain/EDU.GVA.ES"
		self.section_ref_alu="domain/ALU.EDU.GVA.ES"
		self.option_ref="simple_allow_groups"
	
	#def __init__

	def is_access_denied_group_enabled(self):

		is_enabled=os.path.exists(self.group_deny_list_path)

		return n4d.responses.build_successful_call_response(is_enabled)

	#def is_access_denied_group_enabled

	def get_groups_info(self,init_load=True):

		deny_groups=set(self._read_denied_groups_file())
		groups_info=self._read_groups_list(init_load)

		for group_name,group_data in groups_info.items():
			if isinstance(group_data,dict):
				group_data["isLocked"]=group_name in deny_groups

		return n4d.responses.build_successful_call_response(groups_info)

	#def get_groups_info 

	def _read_denied_groups_file(self):

		deny_groups=[]

		if os.path.exists(self.group_deny_list_path):
			try:
				with open(self.group_deny_list_path,'r') as fd:
					for line in fd:
						clean_line=line.strip()
						if clean_line:
							deny_groups.append(clean_line)
			except Exception as e:
				print(f"AccessControlManager._read_denied_groups_file. Error:{e}")
				pass

		return deny_groups

	#def _read_denied_groups_file

	def _read_groups_list(self,init_load):

		template_groups={}
		current_groups={}

		if os.path.exists(self.default_groups_file):
			try:
				with open(self.default_groups_file,'r',encoding='utf-8') as fd:
					current_groups=json.load(fd)
			except Exception as e:
				print(f"AccessControlManager._read_groups_list. Error: {e}")
				pass
		
		if init_load:
			if os.path.exists(self.group_template_path):
				try:
					with open(self.group_template_path) as fd:
						template_groups=json.load(fd)
				except Exception as e:
					print(f"AccessControlManager._read_groups_list. Error: {e}")
					pass

			for item in template_groups:
				template_groups[item]["isLocked"]=False

			if not current_groups:
				self._write_default_group_file(template_groups)
				return template_groups

			needs_update=False
			for group_name,group_data in template_groups.items():
				if group_name not in current_groups:
					current_groups[group_name]=group_data
					needs_update=True

			if needs_update:
				self._write_default_group_file(current_groups)

		for group_name in current_groups:
			if "isLocked" not in  current_groups[group_name]:
				current_groups[group_name]["isLocked"]=False
		
		return current_groups

	#def _read_groups_list

	def set_groups_info(self,groups_info):

		deny_groups=[]
		normalized_groups_info={}

		try:
			if not groups_info:
				return n4d.responses.build_successful_call_response()

			for group_name,group_data in groups_info.items():
				clean_name=group_name.lower()
				normalized_groups_info[clean_name]=group_data

				if group_data.get("isLocked",False):
					deny_groups.append(clean_name)

			self._write_default_group_file(normalized_groups_info)

			if deny_groups:
				with open(self.group_deny_list_path,'w',encoding='utf-8') as fd:
					for group in deny_groups:
						fd.write(f"{group}\n")
				return n4d.responses.build_successful_call_response()
				
			else:
				return self.disable_access_denied_group()
		
		except Exception as e:
			print(f"AccessControlManager.set_groups_info. Error: {e}")
			return n4d.responses.build_failed_call_response(AccessControlManager.SET_GROUP_ERROR)
	
	#def set_groups_info

	def disable_access_denied_group(self):

		try:
			if os.path.exists(self.group_deny_list_path):
				os.remove(self.group_deny_list_path)
		
			return n4d.responses.build_successful_call_response()
		except:
			print(f"AccessControlManager.disable_access_denied_group. Error: {e}")
			return n4d.responses.build_failed_call_response(AccessControlManager.DISABLE_GROUP_ACCESS_CONTROL_ERROR)
	
	#def disable_access_denied_group

	def is_access_denied_user_enabled(self):

		is_enabled=os.path.exists(self.user_denied_list_path)

		return n4d.responses.build_successful_call_response(is_enabled)

	#def is_access_denied_user_enabled

	def get_users_info(self):

		deny_users={user.lower() for user in self._read_denied_users_file()}
		raw_users_list=self._read_users_list()

		normalized_users={}

		for username,user_data in raw_users_list.items():
			clean_name=username.lower()
			normalized_users[clean_name]=user_data
			normalized_users[clean_name]["isLocked"]=clean_name in deny_users

		for blocked_user in deny_users:
			if blocked_user not in normalized_users:
				normalized_users[blocked_user]={"isLocked":True}

		return n4d.responses.build_successful_call_response(normalized_users)

	#def get_users_info 

	def _read_denied_users_file(self):

		deny_users=[]

		if os.path.exists(self.user_denied_list_path):
			try: 
				with open(self.user_denied_list_path,'r') as fd:
					for line in fd:
						clean_line=line.strip()
						if clean_line:
							deny_users.append(clean_line)
			except Exception as e:
				prnit(f"AccessControlManager._read_denied_users_file. Error: {e}")
				pass

		return deny_users

	#def _read_denied_users_file

	def _read_users_list(self):

		users_list={}

		if os.path.exists(self.users_list):
			try:
				with open(self.users_list,'r') as fd:
					users_list=json.load(fd)
			except Exception as e:
				print(f"AccessControlManager._read_users_list. Error: {e}")
				pass

		return users_list

	#def _read_users_list

	def set_users_info(self,users_info):

		deny_users=[]
		normalized_users_info={}

		try:
			if not users_info:
				if os.path.exists(self.users_list):
					os.remove(self.users_list)

				return self.disable_access_denied_user()

			for username,user_data in users_info.items():
				clean_name=username.lower()
				normalized_users_info[clean_name]=user_data

				if user_data.get("isLocked",False):
					deny_users.append(clean_name)

			with open(self.users_list,'w',encoding="'utf-8") as fd:
				json.dump(normalized_users_info,fd)

			if deny_users:
				with open(self.user_denied_list_path,'w',encoding='utf-8') as fd:
					for user in deny_users:
						fd.write(f"{user}\n")

				return n4d.responses.build_successful_call_response()
			else:
				return self.disable_access_denied_user()
		
		except Exception as e:
			print(f"AccessControlManager.set_users_info. Error: {e}")
			return n4d.responses.build_failed_call_response(AccessControlManager.SET_USER_ERROR)
	
	#def set_users_info

	def disable_access_denied_user(self):

		try:
			if os.path.exists(self.user_denied_list_path):
				os.remove(self.user_denied_list_path)
		
			return n4d.responses.build_successful_call_response()
		except Exception as e:
			print(f"AccessControlManager.disable_access_denied_user. Error: {e}")
			return n4d.responses.build_failed_call_response(AccessControlManager.DISABLE_USER_ACCESS_CONTROL_ERROR)
	
	#def disable_access_denied_group

	def _write_default_group_file(self,data):

		with open(self.default_groups_file,'w',encoding='utf-8') as fd:
			json.dump(data,fd)
	
	#def _write_default_group_file

	def is_cdc_access_control_allowed(self):

		is_allowed=os.path.exists(self.sssd_config_path)
	
		return n4d.responses.build_successful_call_response(is_allowed)

	#def is_cdc_access_control_allowed

	def is_access_denied_cdc_enabled(self):

		current_code=self._read_sssd_conf_file()

		is_enabled=bool(current_code and current_code.strip())
				
		return n4d.responses.build_successful_call_response(is_enabled)

	#def is_access_denied_cdc_enabled

	def get_cdc_info(self):

		current_code=self._read_sssd_conf_file()
		cdc_info=self._read_cdc_info()

		clean_code=current_code.strip() if current_code else ""

		if clean_code:
			cdc_info["accessControlEnabled"]=True
			cdc_info["code"]=clean_code

		else:
			cdc_info["accessControlEnabled"]=False
			cdc_info["code"]=""
				
		return n4d.responses.build_successful_call_response(cdc_info)

	#def get_cdc_info

	def set_cdc_info(self,cdc_info):

		try:
			if not cdc_info:
				if os.path.exists(self.cdc_info):
					os.remove(self.cdc_info)
				
				return self.disable_access_denied_cdc()
			
			with open(self.cdc_info,'w',encoding='utf-8') as fd:
				json.dump(cdcInfo,fd)

			if cdc_info.get("accessControlEnabled",False):
				code=cdc_info.get("code","")
				current_code=f'GRP_{code},AdminSai'
				return self._write_sssd_conf_file(current_code)
			else:
				return self.disable_access_denied_cdc()
		
		except Exception as e:
			print(f"AccessControlManager.set_cdc_info. Error: {e}")
			return n4d.responses.build_failed_call_response(AccessControlManager.SET_CDC_ERROR)
	
	#def set_cdc_info

	def disable_access_denied_cdc(self,update_cdc_info=False):

		if update_cdc_info:
			try:
				cdc_info=self._read_cdc_info()
				if cdc_info.get("accessControlEnabled",False):
					cdf_info["accessControlEnabled"]=False
					with open(self.cdc_info,'w',encoding='utf-8') as fd:
						json.dump(cdc_info,fd)
			except Exception as e:
				print(f"AccessControlManager.disable_access_denied_cdc. Error: {e}")
				return n4d.responses.build_failed_call_response(AccessControlManager.DISABLE_CDC_ACCESS_CONTROL_ERROR)

		return self._write_sssd_conf_file()

	#def disable_access_denied_cdc

	def _read_cdc_info(self):

		cdc_info={}

		if os.path.exists(self.cdc_info):
			with open(self.cdc_info,'r') as fd:
				cdc_info=json.load(fd)

		return cdc_info

	#def _read_cdc_info

	def _read_sssd_conf_file(self):

		current_code=""
		

		if not os.path.exists(self.sssd_config_path):
			return current_code

		try:
			configFile=configparser.ConfigParser()
			configFile.optionxform=str
			configFile.read(self.sssd_config_path,encoding='utf-8')

			section_ref=""
			if configFile.has_section(self.section_ref_desa):
				section_ref=self.section_ref_desa
			elif configFile.has_section(self.section_ref_pro):
				section_ref=self.section_ref_pro

			if section_ref and configFile.has_option(section_ref,self.option_ref):
				raw_code=configFile.get(section_ref,self.option_ref)
				if 'GRP_' in raw_code:
					parts=raw_code.split("GRP_")
					if len(parts)>1:
						current_code=parts[1].split(",")[0].strip()
		except Exception as e:
			print(f"AccessControlManager._read_sssd_conf_file. Error: {e}")

		return current_code

	#def _read_sssd_conf_file

	def _write_sssd_conf_file(self,code=""):
		
		sections_to_update=[]
		try:
			if os.path.exists(self.sssd_config_path):
				configFile=configparser.ConfigParser()
				configFile.optionxform=str
				configFile.read(self.sssd_config_path)

				if configFile.has_section(self.section_ref_desa):
					sections_to_update.append(self.section_ref_desa)
				elif configFile.has_section(self.section_ref_pro):
					sections_to_update.append(self.section_ref_pro)
				elif configFile.has_section(self.section_ref_alu):
					sections_to_update.append(self.section_ref_alu)

				if sections_to_update:
					for section in sections_to_update:
						if code:
							configFile.set(section,self.option_ref,code)
						else:
							configFile.remove_option(section,self.option_ref)

					with open(self.sssd_config_path,'w',encoding='utf-8') as fd:
						configFile.write(fd)

			subprocess.run(['systemctl','restart','ssd'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
			return n4d.responses.build_successful_call_response()

		except Exception as e:
			print(f"AccessControlManager._write_sssd_conf_file. Error: {ẽ}")
			return n4d.responses.build_failed_call_response(AccessControlManager.SET_CDC_ERROR)
		
	#def _write_sssd_conf_file 

#class AccessControlManager 

