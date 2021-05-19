import socket

import socket, signal, sys, select, os

server_ip = [socket.gethostbyname("samuel.freetcp.com"), "127.0.0.1"]
server_port = 9993
server = -1
MSG_SIZE = 1024

VLINE=chr(9474)
username=''


def exit_sig(sig=0, frame=0):
    client.close()
    exit(0)




while(not 0<=server<len(server_ip)):
    server = int(input("Select server:\n0: Remote Server\n1: Localhost\n"))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((server_ip[server], server_port))
except:
    print("ERROR: Server {} is offline".format(server_ip[server]))
    client.close()
    exit(1)

signal.signal(signal.SIGINT, exit_sig)
inputs = [client, sys.stdin]
message=''
print("COMMAND: ",  end='')
sys.stdout.flush()
while True:
    ins, outs, exs = select.select(inputs, [], [])
    for i in ins:
        if(i==sys.stdin):
            response=sys.stdin.readline()
            client.sendto(response.encode(),(server_ip[server],server_port))
        elif(i==client):
            (server_msg, addr) = client.recvfrom(MSG_SIZE)
            if(not server_msg):
                exit_sig()
            message+=str(server_msg.decode())
            if(message[-1]!='\n'):
                continue
            message=message.split('\n')
            for k in message:
                process_input(k)
            message=''
            print("{}COMMAND: ".format(username), end='')
            sys.stdout.flush()