
import socket, sys
import threading

bind_ip = '127.0.0.1'
bind_port = 9993

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))
server.listen(5)  # max backlog of connections

print ('Listening on {}:{}'.format(bind_ip, bind_port))


def handle_client_connection(client_socket):
    msg_from_client = client_socket.recv(1024)
    request = msg_from_client.decode()
    print ('Received {}'.format(request))
    msg_to_client='ACK'.encode()
    print (msg_to_client)
    client_socket.send(msg_to_client)
    client_socket.close()


def main():
    global server
    server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_address, bind_port))
    server.listen(100);
    print("Listening on {}:{}".format(bind_address, bind_port))
    signal.signal(signal.SIGINT, exit_server)
    while  True:
        client_sock, address = server.accept()
        print("Acepted connection from {}:{}".format(address[0],address[1]))
        client_handler=threading.Thread(target=handle_client_connection, args=(client_sock, ))
        client_handler.start()

