# SSH_commander
A simple script to execute system commands through SSH on multiple hosts

## Dependencies and python version
SSH Commander depends on the **paramiko** library. No more.
It runs under **Python 2.7**. I live in the past.

## Usage
```
python ssh_commander.py -h

== SSH commander script ==
usage: ssh_deploy.py [-h] [-c COMMAND [COMMAND ...]] [-u] [-U]
                     [-f HOST_LIST_FILE] [--hosts ETC_HOSTS_LIST]

Command execution on multiple hosts

optional arguments:
  -h, --help            show this help message and exit
  -c COMMAND [COMMAND ...], --command COMMAND [COMMAND ...]
                        run a command
  -u, --update          update systems
  -U, --upgrade         update && upgrade systems
  -f HOST_LIST_FILE, --file HOST_LIST_FILE
                        host list file
  --hosts ETC_HOSTS_LIST
                        use /etc/hosts
```
+ Specify the command using **-c**
+ Use a host file list using **-f**
+ Or your /etc/hosts file using **--hosts**
+ You can also update or upgrade the systems using **-u** or **-U**

## Host file list
The host file list has the following structure:
```
user@IP:port password=pass id_rsa=path/to/priv_key
```
Only the IP is mandatory, default values for other fileds are:
+ user: root
+ port: 22
+ pass: *blank*
+ id_rsa: *~/.ssh/id_rsa*

If no password is specified, the private key is used.
An example file is included as **hostlist_example.txt**.

## Troubles and ameliorations
You are free to contribute to this project by reporting troubles and suggestions.
Every code amelioration is welcome.
Moreover, you are free to fork the code and go on your way !
