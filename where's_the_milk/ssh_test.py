'''
Code structure below from: https://www.linode.com/docs/guides/use-paramiko-python-to-ssh-into-a-server/
'''

import paramiko
import sys

command = "ls"

# Update the next three lines with your
# server's information

host = "10.0.0.187"
username = "pi"
password = "Fobbay4818!"

client = paramiko.client.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, username=username, password=password)
_stdin, _stdout,_stderr = client.exec_command(command)
print(_stdout.read().decode())
client.close()