import socket, sys
import threading

server_ip = '127.0.0.2'
server_port = 9993
buffer = 4096

#hostname, sld, tld, port = 'www', 'integralist', 'co.uk', 80
hostname, sld, tld, port = 'www', 'tecnico', 'ulisboa.pt', 80
target = '{}.{}.{}'.format(hostname, sld, tld)
print ('target', target)


def main():
    # create an ipv4 (AF_INET) socket object using the tcp protocol (SOCK_STREAM)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # connect the client
        # client.connect((target, port))
        client.connect((server_ip, server_port))
    except:
        print("server out of service")
        client.close()
        exit(1)


    while True:
        
        msg = sys.stdin.readline()
        
        if(msg != None):
            # send some data (in this case a HTTP GET request)
            client.send(msg.encode())
            # receive the response data (4096 is recommended buffer size)
            response = client.recv(buffer)
            decoded_response = response.decode()
            print(decoded_response)
    
if(__name__ == '__main__'):
    main()



  


