import socket, signal, sys, select, os

server_ip = '127.0.0.1'
server_port = 9993

hostname, sld, tld, port = 'www', 'tecnico', 'ulisboa.pt', 80
target = '{}.{}.{}'.format(hostname, sld, tld)
print ('target', target)




def exit_sig(sig=0, frame=0):
    client.close()
    exit(0)


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    client.connect((server_ip, server_port))
except:
    print("ERROR: Server {} is offline".format(server_ip))
    client.close()
    exit(1)
    

signal.signal(signal.SIGINT, exit_sig)
inputs = [client, sys.stdin]
message=''
print("COMMAND: ")
sys.stdout.flush()
    
while True:
    ins, outs, exs = select.select(inputs, [], [])
    for i in ins:
        if(i==sys.stdin):
            response=sys.stdin.readline()
            client.sendto(response.encode(),(server_ip ,server_port))
        elif(i==client):
            (server_msg, addr) = client.recvfrom(4096)
            if(not server_msg):
                exit_sig()
            message+=str(server_msg.decode())
            if(message[-1]!='\n'):
                continue
            message=message.split('\n')
            for k in message:
                print(k)
                if(k=="SERVER_OFF"):
                    sys.stdout.flush()
                    exit_sig()
            message=''
            sys.stdout.flush()
