import socket, sys, threading, signal, os
from threading import RLock


server = -1
bind_ip = '127.0.0.1'
bind_port = 9993
connections=[]
lock = RLock()


MAX_MSG =1024
MAX_ACTIV= 100

#mensagens de OK
OK_LOC_REGIST = "{} Local registado.\n"
OK_BALANCE = "Saldo Atual : {}.\n"
OK_CANCEL_LOC = "1 Registo local foi cancelado.\n"
OK_CR_ACTIV = "{} Atividade Criada.\n"
OK_MOD_ACTIV ="1 Atividade Modificada.\n"
OK_REM_ACTIV = "1 Atividade Removida.\n"

#mensagens de erro
ERR_REGIST_LOC_INFO = "0 Registo de Local: falta de paramêtros.\n"
ERR_REGIST_LOC_EXIST= "0 Registo de Local: o local já existe.\n"
ERR_REGIST_LOC_NOINFO = "0 Registo de Local: sem paramêtros.\n"
ERR_REGIST_LOC_MAXINFO = "0 Registo de Local: paramêtros a mais.\n"

ERR_SALDO_NEXIST = "0 Consulta de Saldo: o Local não existe.\n"
ERR_SALDO_TOMUCHINFO = "0 Consulta de Saldo: paramêtros a mais.\n"
ERR_SALDO_NOINFO = "0 Consulta de Saldo: paramêtros em falta.\n"

ERR_CANCEL_LOC_NEXIST = "0 Cancelamento de Registo: o local não existe.\n"
ERR_CANCEL_LOC_NOINFO =  "0 Cancelamento de Registo: sem paramêtros.\n"
ERR_CANCEL_LOC_INFO =  "0 Cancelamento de Registo: falta de paramêtros.\n"

ERR_CR_ACTIV_NOINFO = "0 Criação de atividade:sem paramêtros.\n"
ERR_CR_ACTIV_INFO  = "0 Criação de atividade:falta de paramêtros.\n"
ERR_CR_ACTIV_MAXINFO = "0 Criação de atividade:paramêtros a mais.\n"
ERR_CR_ACTIV_NEXIST = "0 Criação de atividade: local nao existe\n"
ERR_CR_ACTIV_TYPE = "0 Criação de atividade: atividade do mesmo tipo já existe.\n"
ERR_CR_ACTIV_LIMIT = "0 Criação de atividade: limite maximo de atividades atingido\n"

ERR_MOD_ACTIV_NEXIST = "0 Modificação de atividade:  atividade não existe.\n"
ERR_MOD_ACTIV_INFO = "0 Modificação de atividade:falta de paramêtros.\n"
ERR_MOD_ACTIV_ONGOING = "0 Modificação de atividade: atividade a decorrer.\n"
ERR_MOD_ACTIV_NOINFO = "0 Modificação de atividade: sem paramêtros.\n"
ERR_MOD_ACTIV_MAXINFO = "0 Modificação de atividade:paramêtros a mais.\n"

ERR_REM_ACTIV_NEXIST = "0 Remoção de atividade: atividade não existente.\n"
ERR_REM_ACTIV_ONGOING =  "0 Remoção de atividade: Atividade a decorrer.\n"
ERR_REM_ACTIV_NOINFO = "0 Remoção de atividade: sem paramêtros.\n"
ERR_REM_ACTIV_INFO = "0 Remoção de atividade: paramêtros em falta.\n"
ERR_REM_ACTIV_MAXINFO = "0 Remoção de atividade: paramêtros a mais.\n"

#funcao que recebe um signal e mata o servidor e todos os seus clientes
def exit_server(sig=0, frame=0):
    print("\nExiting server recieved signal {}...".format(sig))
    server.close()
    for c in connections:
        c.send("SERVER_OFF\n".encode())
        c.close()
    exit(0)


#funcao que regista um local
def registar(k):
    loc_id = 0
    output = ' '
    if len(k)== 0:
        return ERR_REGIST_LOC_NOINFO

    if len(k)<4:
        return ERR_REGIST_LOC_INFO

    if len(k)<4:
        return ERR_REGIST_LOC_MAXINFO

    if (type(k[1])!= int or type(k[2])!=int or type(k[3])!= int):
        return ERR_REGIST_LOC_INFO

    f = open("locals.txt", "r")
    for e in f:
        checker = e.strip('\n').split(" ")
        if loc_id  < int(checker[0]):
            loc_id = int(checker[0])
        if checker[1] == k[0]:
            return ERR_REGIST_LOC_EXIST
    f.close() 

    f = open("locals.txt", "a")
    for e in k:
        output += e + ' '
    loc_id += 1
    res = str(loc_id) + output+  '\n'
    f.write(res)
    f.close()
    return OK_LOC_REGIST.format(str(loc_id))

def consultar_saldo(k):

    if len(k) == 0:
        return ERR_SALDO_NOINFO

    if len(k) > 1:
        return ERR_SALDO_TOMUCHINFO

    f = open("locals.txt", "r")
    for e in f:
        checker = e.strip('\n').split(" ")
        if checker[1] == k[0]:
            saldo = checker[4]
            f.close()
            return OK_BALANCE.format(saldo)
    f.close()
    return ERR_SALDO_NEXIST

def cancelar_registo(k):
    temp_loc= ''
    temp_act = ''
    temp_client = ''
    counter = 0
    aviso = ''

    if len(k) == 0:
        return ERR_CANCEL_LOC_NOINFO

    if k[0] == '':
        return ERR_CANCEL_LOC_INFO


    f = open("locals.txt", "r")
    for e in f:
        checker = e.split(" ")
        if checker[1] == k[0]:
            counter += 1
        else:
           temp_loc += e 
    f.close()
    if counter == 0:
        return ERR_CANCEL_LOC_NEXIST

    a = open("avisos.txt", 'a')
    c = open("clients.txt", "r")
    for u in c:
        client_check = u.split(" ")
        if client_check[1] == k[0]:
            aviso = client_check[0] + ' ' + client_check[2] + "\n"
            a.write(aviso)
            aviso = ''
        else:
            temp_client += u 
    c.close()

    r = open("activities.txt","r")
    for i in r:
        checker_act = i.split(" ")
        if checker_act[1] != k[0]:
            temp_act += i 
    r.close()

    f = open("locals.txt", "w")
    f.write(temp_loc)
    f.close()
    c = open("clients.txt", "w")
    c.write(temp_client)
    c.close()
    r = open("activities.txt","w")
    r.write(temp_act)
    r.close()
    return OK_CANCEL_LOC

def criarAtividade(k):
    global MAX_ACTIV
    counter = 0
    a_id = 0
    output= ''
    exist_counter = 0

    if(len(k)==0):
        return ERR_CR_ACTIV_NOINFO
    if(len(k)<7):
        return ERR_CR_ACTIV_INFO
    if (len(k)>7):
        return ERR_CR_ACTIV_MAXINFO


    f = open("activities.txt", "r") 
    for e in f:
        act_checker = e.split(" ")
        if act_checker[1] == k[0] and act_checker[2] == k[1]:
            return ERR_CR_ACTIV_TYPE
        if (a_id < int(act_checker[0])):
            a_id = int(act_checker[0])

    t = open("locals.txt", "r")
    for i in t:
            loc_check = i.split(" ")
            if loc_check[1] == k[0]:
                exist_counter += 1
    
    t.close()
    f.close()

    if exist_counter == 0:
        return ERR_CR_ACTIV_NEXIST
    if a_id == MAX_ACTIV:
        return ERR_CR_ACTIV_LIMIT
    
    f = open("activities.txt", "a")
    for e in k:
        output += e +' '
    a_id += 1
    res = str(a_id)+ ' ' + output+  '\n'
    f.write(res)
    f.close()
    return OK_CR_ACTIV.format(str(a_id))

def modificarAtividade(k):
    counter = 0
    temp = ''
    old_line = ''

    if len(k) == 0:
        return ERR_MOD_ACTIV_NOINFO
    if len(k) < 4 :
        return ERR_MOD_ACTIV_INFO
    if len(k) > 4 :
        return ERR_MOD_ACTIV_MAXINFO
    

    f = open("activities.txt", "r")
    for e in f:
        checker = e.split(" ")
        if checker[2] == k[0]:
            counter +=1
            old_line = e
        else:
            temp += e
    f.close()

    if counter == 0:
        return ERR_MOD_ACTIV_NEXIST


    new = old_line.split(" ")
    old_line =''
    new[4] = k[1]
    new[6] = k[2]
    new[7] = k[3] +"\n"
    for e in new:
        old_line += e + ' '

    temp += old_line

    f = open("activities.txt", "w")
    f.write(temp)
    f.close()
    return OK_MOD_ACTIV


def removerAtividade(k):
    counter = 0
    temp = ''
    if (len(k)== 0):
        return ERR_REM_ACTIV_NOINFO
    if k[0] == '':
        return ERR_REM_ACTIV_INFO
    if (len(k)> 1):
        return ERR_REM_ACTIV_MAXINFO

    f = open("activities.txt", "r")
    for e in f:
        checker = e.split(" ")
        if k[0] == checker[2]:
            counter += 1
        else:
            temp += e
    f.close()

    if counter == 0:
        return ERR_REM_ACTIV_NEXIST

    f = open("activities.txt", "w")
    f.write(temp)
    f.close()
    return OK_REM_ACTIV

def process_input(k, client_sock):
    k = k.strip('\n').split(" ")
    print("Recieved >{}<".format(k))
    if(k[0] == "REGISTAR_LOCAL"):
        k.pop(0)
        return registar(k)
    if(k[0] == "CONSULTAR_SALDO"):
        k.pop(0)
        return consultar_saldo(k)
    if(k[0] == "CANCELAR_REGISTO"):
        k.pop(0)
        return cancelar_registo(k)
    if(k[0] == "CRIAR_ATIVIDADE"):
        k.pop(0)
        return criarAtividade(k)
    if(k[0] == "MODIFICAR_ATIVIDADE"):
        k.pop(0)
        return modificarAtividade(k)
    if(k[0] == "REMOVER_ATIVIDADE"):
        k.pop(0)
        return removerAtividade(k)
    return "COMANDO INVALIDO\n"


def handle_client_connection(client_sock):
    signal.pthread_sigmask(signal.SIG_SETMASK, [signal.SIGINT, signal.SIGKILL])
    try:
        with lock:
            connections.append(client_sock)
        while True:
            request=''
            #soma strings ate ter mensagem completa
            while(request=='' or request[-1]!='\n'):
                msg_from_client = client_sock.recv(MAX_MSG)
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