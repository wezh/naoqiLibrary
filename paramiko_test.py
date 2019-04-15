import paramiko

scp = paramiko.Transport(('192.168.1.105', 22))
#Establish connection
scp.connect()