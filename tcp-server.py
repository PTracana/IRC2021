import socket, sys, threading, signal, os
from threading import RLock



bind_address    = ''
bind_port       = 9993
server = 0
connections=[]
lock = RLock()




def exit_server(sig, frame):
    print("\nExiting server recieved signal {}...".format(sig))
    server.close()
    for c in connections:
        c.send("SERVER_OFF\n".encode())
        c.close()
    exit(0)


def handle_client_connection(client_sock):
    signal.pthread_sigmask(signal.SIG_SETMASK, [signal.SIGINT, signal.SIGKILL])
    try:
        with lock:
            connections.append(client_sock)
        while True:
            request=''
            #soma strings ate ter mensagem completa
            while(request=='' or request[-1]!='\n'):
                msg_from_client = client_sock.recv(1024)
                if(not msg_from_client):
                    raise socket.timeout()
                request += str(msg_from_client.decode())
            with lock:
                client_sock.send(process_input(request, client_sock).encode())
    except socket.timeout:
        with lock:
            for i in range(len(connections)):
                if(connections[i]==client_sock):
                    del(connections[i])
                    break
        client_sock.close()
        print("Client disconected".format(client_sock))
        exit(0)




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
#----

if(__name__ == '__main__'):
    main()