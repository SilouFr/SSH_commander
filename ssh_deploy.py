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
	cut_index = hosts_list.index("# --- END PVE ---") #index of "END PVE"
	hosts_list = hosts_list[cut_index+1:] #all lines after this index
	#print hosts_list, len(hosts_list)

	array_list = []
	for line in hosts_list:
		if " " in line:
			one_machine = line.split(" ")
		if "\t" in line:
			one_machine = line.split("\t")

		array_list.append(one_machine)

	print "[+]", len(array_list), "machines loaded from", hosts_file

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
	hosts = import_etc_hosts()

	default_user = "root"
	default_port = 22
	key_path = "/home/admin/.ssh/id_rsa"

	#script arguments parsing
	parser = argparse.ArgumentParser(description="Command execution on multiple hosts")
	parser.add_argument('-c', "--command", action="store", help="run a command", dest="command", nargs="+")
	parser.add_argument('-u', '--update', action="store_true", help="update CTs", dest="update")
	parser.add_argument('-U', '--upgrade', action="store_true", help="update && upgrade CTs", dest="upgrade")

	try:
		arguments = parser.parse_args()
	except:
		parser.print_help()
		sys.exit(0)

	global client_connection
	command = ""

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
	#index to connect to every server in the list EXCEPT the first one which is the GW
	for i in range(1, len(hosts)):
		index = str(i)+"/"+str(len(hosts))
		connect_to_host(hosts[i][1], default_port, default_user, key_path, index)
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

	if arguments.upgrade:
		print bcolors.BOLD + "don't forget to run upgrade on this machine"


#tests area
main()
