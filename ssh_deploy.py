#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import paramiko
import traceback
import socket
import argparse
import datetime
import select

global client_connection

#terminal colors
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


#import hosts from host file
def import_etc_hosts():

	hosts_file = "/etc/hosts"
	hosts_list = open(hosts_file, 'r').readlines() #read /etc/hosts
	hosts_list = map(str.rstrip, hosts_list) #remove \r and \n
	hosts_list = filter(None, hosts_list) #remove empty elements

	array_list = []
	for line in hosts_list:
		if " " in line:
			one_machine = line.split(" ")
		if "\t" in line:
			one_machine = line.split("\t")

		array_list.append(one_machine)

	print "[+]", len(array_list), "machines loaded from", hosts_file

	return array_list

def import_host_list(host_list_file):
	#relative path
	if host_list_file[0] != "/":
		host_list_file = os.getcwd() + "/" + host_list_file

	host_list = open(host_list_file, 'r').readlines() #read /etc/hosts
	host_list = map(str.rstrip, host_list) #remove \r and \n
	host_list = filter(None, host_list) #remove empty elements

	array_list = []
	for line in host_list:
		host_configuration = [""] * 4
		params = None

		#split the line
		if " " in line:
			host_info, params = line.split(" ")
		else:
			host_info = line

		#username
		if "@" in host_info:
			host_username, host_info = host_info.split("@")
			host_configuration[0] = host_username
		
		#port
		if ":" in host_info:
			host_ip, host_port = host_info.split(":")
			host_configuration[1] = host_ip
			host_configuration[2] = host_port
		else:
			host_ip = host_info
			host_configuration[1] = host_ip

		if params is not None:
			#password provided
			if "password" in params:
				host_password = params.split("=")[1]
				host_configuration[3] = "pass:"+host_password

			#id_rsa provided, relative or not
			elif "id_rsa" in params:
				host_id_rsa = params.split("=")[1]
				if host_id_rsa[0] != "/":
					host_configuration[3] = "id_rsa:" + os.getcwd() + "/" + host_id_rsa
				else:
					host_configuration[3] = "id_rsa:" + host_id_rsa

		array_list.append(host_configuration)
	print "[+]", len(array_list), "machines loaded from", host_list_file
	return array_list


def connect_to_host(hostname, port, username, key_file, index):
	global client_connection

	key = paramiko.RSAKey.from_private_key_file(key_file)
	client_connection = paramiko.SSHClient()
	client_connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	client_connection.connect(hostname, port, username, pkey = key )
	print bcolors.BOLD + "\n[+]["+index+"] connected to "+str(username)+"@"+str(hostname)+":"+str(port) + bcolors.ENDC


def run_command(command):
	global client_connection
	user_input = ""

	#stdin/out/err
	stdin, stdout, stderr = client_connection.exec_command(command)
	read_stdin = select.select([sys.stdin], [], [], 0)[0]

	print "$ > "+str(command)

	#console output
	for line in stdout:
		print(line.strip('\n'))

	#console errors
	for line in stderr:
		print bcolors.FAIL + line.strip('\n') + bcolors.ENDC

	#ERROR
	if stderr.read():
		return "0"

	if sys.stdin in read_stdin:
		user_stdin = sys.stdin.readline()
		print "received user input: ",user_stdin
		stdin.write(user_stdin)
		print "stdin written"
		stdin.flush()

	#no error
	else:
		return 1


def main():
	print "== SSH commander script =="

	paramiko.util.log_to_file('ssh_commander.log')

	#defaults
	default_user = "root"
	default_port = 22
	default_key_path = os.path.expanduser("~/.ssh/id_rsa")

	#script arguments parsing
	parser = argparse.ArgumentParser(description="Command execution on multiple hosts")
	parser.add_argument('-c', "--command", action="store", help="run a command", dest="command", nargs="+")
	parser.add_argument('-u', '--update', action="store_true", help="update systems", dest="update")
	parser.add_argument('-U', '--upgrade', action="store_true", help="update && upgrade systems", dest="upgrade")
	parser.add_argument('-f', "--file", action="store", help="host list file", dest="host_list_file")
	parser.add_argument("--hosts", action="store", help="use /etc/hosts", dest="etc_hosts_list")

	try:
		arguments = parser.parse_args()
	except:
		'''parser.print_help()'''
		sys.exit(0)

	global client_connection
	command = ""
	hosts = ""

	#list from aribtrary file
	if arguments.host_list_file:
		host_list_file = arguments.host_list_file
		hosts = import_host_list(host_list_file)
	

	#list from /etc/hosts
	if arguments.etc_hosts_list:
		etc_hosts_list = arguments.etc_hosts_list		
		hosts = import_etc_hosts()

	#execute a simple command
	if arguments.command:
		command = ' '.join(arguments.command)

	#run source update 
	elif arguments.update:
		command = "aptitude update"

	#run system upgrade
	elif arguments.upgrade:
		command = "DEBIAN_FRONTEND=noninteractive aptitude safe-upgrade -yq"

	#how ?
	else:
		print "[-] please provide at least one argument"
		parser.print_help()
		sys.exit(0)


	command_success = 0
	command_error = 0


	for i in range(len(hosts)):
		index = str(i)+"/"+str(len(hosts))
		connect_to_host(hosts[i][1], default_port, default_user, default_key_path, index)
		command_exec = run_command(command)

		#stats for success/fail
		if command_exec == 1:
			command_success +=1
		else:
			command_error += 1
		client_connection.close()
	
	#some stats about success/fails
	print "\n\n[=] STATS :"
	print bcolors.OKGREEN + "success :", command_success, bcolors.ENDC
	print bcolors.FAIL + "errors :", command_error, bcolors.ENDC


main()