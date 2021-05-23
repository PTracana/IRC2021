import socket, sys, threading, signal, os
from threading import RLock


server = -1
bind_ip = '127.0.0.1'
bind_port = 9993
connections=[]
lock = RLock()


#mensagens de OK
OK_LOC_REGIST = "{} Local registado.\n"
OK_BALANCE = "Saldo Atual : {}.\n"
OK_CANCEL_LOC = "1 Registo local foi cancelado.\n"
OK_CR_ACTIV = "{} Atividade Criada.\n"
OK_MOD_ACTIV ="1 Atividade Modificada.\n"
OK_REM_ACTIV = "1 Atividade Removida.\n"

#mensagens de erro
ERR_REGIST_LOC_INFO = "0 Registo de Local: falta de informação.\n"
ERR_REGIST_LOC= "0 Registo de Local: o local já existe.\n"
ERR_CANCEL_LOC = "0 Cancelamento de Registo: o local não existe.\n"
ERR_CR_ACTIV_TYPE = "0 Criação de atividade: atividade do mesmo tipo já existe.\n"
ERR_CR_ACTIV_LIMIT = "0 Criação de atividade: limite maximo de atividades atingido\n"
ERR_MOD_ACTIV_NEXIST = "0 Modificação de atividade:  atividade não existe\n"
ERR_MOD_ACTIV_INFO = "0 Modificação de atividade: falta de informação\n"
ERR_MOD_ACTIV_ONGOING = "0 Modificação de atividade: atividade a decorrer\n"
ERR_REM_ACTIV_NEXIST = "0 Remoção de atividade: atividade não existente\n"
ERR_REM_ACTIV_ONGOING =  "0 Remoção de atividade: Atividade a decorrer\n"

def exit_server(sig=0, frame=0):
    print("\nExiting server recieved signal {}...".format(sig))
    server.close()
    for c in connections:
        c.send("SERVER_OFF\n".encode())
        c.close()
    exit(0)

def process_input(k, client_sock):
    k = k.split(" ")

    return k






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
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)  # max backlog of connections
    print("Listening on {}:{}".format(bind_ip, bind_port))
    signal.signal(signal.SIGINT, exit_server)
    while  True:
        client_sock, address = server.accept()
        print("Acepted connection from {}:{}".format(address[0],address[1]))
        client_handler=threading.Thread(target=handle_client_connection, args=(client_sock, ))
        client_handler.start()
#----

if(__name__ == '__main__'):
    main()