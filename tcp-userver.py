import socket, sys, threading, random
from threading import RLock

bind_ip = '127.0.0.2'
bind_port = 9993
buffer = 4096

#mensagens OK
OK = "OK: "
REG_SUC = " Utente registado com sucesso.\n"
MOD_SUC = "1 Utente modificado.\n"
REM_SUC = "1 Utente removido.\n"

#mensagens ERROR
ERRO = "ERROR: "
FLT_INF = "devido a falta de informação.\n"
ERR_REQ = "Requerimento errado.\n"
REG_ERR_1 = "0 registo de utente recusado: devido a falta de informação.\n"
REG_ERR_2 = "0 registo de utente recusado: devido à existência de um utente com o mesmo nome neste local.\n"
REG_ERR_3 = "0 registo de utente recusado: devido a este local ter a lotação máxima.\n"
MOD_ERR_1 = "0 a alteração não foi permitida: devido a não existir o utente identificado.\n"
MOD_ERR_2 = "0 a alteração não foi permitida: devido a falta de informação.\n"
MOD_ERR_3 = "0 a alteração não foi permitida: devido ao facto do utente se encontrar a participar numa atividade.\n"
REM_ERR_1 = "0 o utente com esse identificador não existe.\n"
REM_ERR_2 = "0 o utente com esse identificador encontra-se numa atividade.\n"
PED_AT_ERR_1 = "0 a atividade não é possível de se realizar devido a perfil inadequado.\n"
PED_AT_ERR_2 = "0 a atividade não é possível de se realizar devido a lotação esgotada.\n"
PED_AT_ERR_3 = "0 a atividade não é possível de se realizar devido a vias de “fecho” neste local.\n"
RCL_ERR_1 = "0 a sua reclamação não foi registada devido a falta de informação.\n"
RCL_ERR_2 = "0 a sua reclamação não foi registada devido há inexistência do registo do local.\n"


client_sockets = []

activity_tracker = [[0] * 100] * 50

rlock = RLock()

def str_veracity(str_temp):
    return isinstance(str_temp, str)

def int_veracity(int_temp):
    return isinstance(int_temp, int)


def register_client(req):
    response = ""
    max_utente_id = 0
    num_lotacao = 0

    if(len(req) != 7):
        response = ERRO + FLT_INF 
        return response

    try:                   #verifica se algum dos dados inseridos que deveriam ser intengers e de outro tipo 
        i = int(req[4])
        i = int(req[5])
        i = int(req[6])
    except ValueError:
        return ERRO + REG_ERR_1

    if(not str_veracity(req[1])):
        response = ERRO + REG_ERR_1
        return response
    elif(not str_veracity(req[2])):
        response = ERRO + REG_ERR_1
        return response
    elif(not str_veracity(req[3])):
        response = ERRO + REG_ERR_1
        return response
    elif(not int_veracity(int(req[4]))):
        response = ERRO + REG_ERR_1
        return response
    elif(not int_veracity(int(req[5]))):
        response = ERRO + REG_ERR_1
        return response
    elif(not int_veracity(int(req[6]))):
        response = ERRO + REG_ERR_1
        return response 

    f = open("activities.txt", "r")
    l = f.readlines()
    f.close()

    for j in range(len(l)):                                     #conta a lotacao total em cada atividade associada a um local
        temp = l[j].split()                                     #e soma tudo
        if(temp[1] == req[1]):
            num_lotacao += activity_tracker[int(temp[0])][0]
    
    f = open("locals.txt", "r")
    l = f.readlines()
    f.close()

    for j in range(len(l)):                                     #encontra o local pretendido no file e verifica se o numero
        temp = l[j].split()                                     #total calculado anteriormente e igual a lotacao maxima 
        if(temp[1] == req[1]):                                  #desse local       
            if(int(temp[2])==num_lotacao):                      #se for esse o caso entao o cliente nao se pode registar nesse local
                response = ERRO + REG_ERR_3
                return response

    f = open("clients.txt", "r")
    l = f.readlines()
    f.close()

    for j in range(len(l)):                                     #encontra o maior id de um Utente registado até ao momento
        temp = l[j].split()
        if(int(temp[0])>max_utente_id):
            max_utente_id = int(temp[0])
        if(req[1] == temp[1] and req[2] == temp[2]):
            return ERRO + REG_ERR_2

    max_utente_id += 1 

    f = open("clients.txt", "a")
    f.write(str(max_utente_id)+" "+req[1]+" "+req[2]+" "+req[3]+" "+str(req[4])+" "+str(req[5])+" "+str(req[6])+" "+"0\n")
    f.close()

    response = OK + "id_U:" + str(max_utente_id) + REG_SUC
    
    return response


def update_client(req):
    response = ""
    utente_id_t = 0
    line_temp = [None] * 8

    if(len(req) != 4):
        response = ERRO + FLT_INF  
        return response

    try:                                   #verifica que nao ha elementos a mais inseridos na funcao
        i = req[3]
    except IndexError:
        return ERRO + MOD_ERR_2   

    try:                                   #verifica se algum dos dados inseridos que deveriam ser intengers e de outro tipo 
        i = int(req[1])         
        i = int(req[3])
    except ValueError:
        return ERRO + MOD_ERR_2

    if(not str_veracity(req[2])):
        response = ERRO + MOD_ERR_2
        return response
    elif(not int_veracity(int(req[1]))):
        response = ERRO + MOD_ERR_2
        return response
    elif(not int_veracity(int(req[3]))):
        response = ERRO + MOD_ERR_2
        return response

    f = open("clients.txt", "r")
    l = f.readlines()
    f.close()

    for j in range(len(l)):                         
        temp = l[j].split()
        if(int(temp[0]) == int(req[1])):          #verifica se um utente ja se encontra numa atividade
            if(int(temp[7]) == 1):
                response = ERRO + MOD_ERR_3
                return response
            line_temp[0] = temp[0]                #guarda os elementos do registo de um cliente
            line_temp[1] = temp[1]                #com as alteracoes pedidas
            line_temp[2] = temp[2]
            line_temp[3] = req[2]
            line_temp[4] = temp[4]
            line_temp[5] = temp[5]
            line_temp[6] = req[3]
            line_temp[7] = temp[7]
            utente_id_t = int(temp[0]) 
            x = j

    if(utente_id_t == 0):                         #se o utente nao existir entao esta condicao devolve um erro
        response = ERRO + MOD_ERR_1
        return response    

    del l[x]                                      #apaga linha antiga que foi modificada

    new_f = open("clients.txt", "w+")             

    for line in l:                                #escreve todas as linhas no file menos a modificada
        new_f.write(line)
    new_f.close()

    f_2 = open("clients.txt", "a")                #acrescenta linha modificada
    f_2.write(line_temp[0]+" "+line_temp[1]+" "+line_temp[2]+" "+line_temp[3]+" "+line_temp[4]+" "+line_temp[5]+" "+line_temp[6]+" "+line_temp[7]+"\n")
    f_2.close()

    response = OK + MOD_SUC

    return response

def remove_client(req):
    response = ""
    utente_id_t = 0
    
    if(len(req) != 2):
        response = ERRO + FLT_INF  
        return response

    try:
        i = int(req[1])
    except ValueError:
        return ERRO + ERR_REQ

    if(not int_veracity(int(req[1]))):
        response = ERRO + ERR_REQ
        return response
    
    f = open("clients.txt", "r")
    l = f.readlines()
    f.close()

    for j in range(len(l)):                          #verifica se o utente existe
        temp = l[j].split()
        if(int(temp[0]) == int(req[1])):           
            if(int(temp[7]) == 1):                   #verifica se o utente se encontra numa atividade 
                response = ERRO + REM_ERR_2
                return response    
            utente_id_t = int(temp[0])
            x = j

    if(utente_id_t == 0):
        response = ERRO + REM_ERR_1
        return response

    del l[x]                                        #remove o registo do utente

    new_f = open("clients.txt", "w+")

    for line in l:
        new_f.write(line)
    new_f.close()
    
    response = OK + REM_SUC

    return response

def check_activities(req):
    response = ""
    m = 0
    n = 0
    
    f = open("activities.txt", "r")
    l = f.readlines()
    f.close()

    f = open("locals.txt", "r")
    l_2 = f.readlines()
    f.close()

    if(len(req) != 1):
        response = ERRO + ERR_REQ 
        return response

    for i in range(len(l)):                                     
        temp = l[i].split()
        for j in range(len(l_2)):
            temp_2 = l_2[j].split()
            if(temp[1] == temp_2[1]):                        
                if(activity_tracker[int(temp[0])][0] != 0):     #verifica se a atividade esta em curso ou nao
                    m = 1
                n = int(temp[4]) - activity_tracker[int(temp[0])][0]        #verifica a disponibilidade de uma atividade
                response += "id_A:"+temp[0]+" id_L:"+temp_2[0]+" Tipo Atividade:"+temp[2]+" Estado:"+str(m)+" Disponibilidade:"+str(n)+" Custo:"+temp[7]+"\n"

    return response


def request_activity(req): #falta o erro 3
    response = ""
    prof_temp = ""
    lot_temp = 0
    dur_temp = 0
    line_temp = [None] * 8
    max_activity_id = 0

    if(len(req) != 3):
        response = ERRO + FLT_INF  
        return response

    try:
        i = int(req[1])
        i = int(req[2])
    except ValueError:
        return ERRO + ERR_REQ

    if(not int_veracity(int(req[1]))):
        response = ERRO + ERR_REQ
        return response
    elif(not int_veracity(int(req[2]))):
        response = ERRO + ERR_REQ
        return response
    

    f = open("activities.txt", "r")
    l = f.readlines()
    f.close()

    if(int(req[1]) == 0):                                       #este loop encontra o numero maximo de atividades e de seguida
        for j in range(len(l)):                                 #atualiza o req_1 para um numero random caso este fosse 0 
            temp = l[j].split()
            if(int(temp[0])>max_activity_id):
                max_activity_id = int(temp[0])
        req[1] = str(random.randint(1,max_activity_id))

    for j in range(len(l)):                                 #verifica se existem atividades 
        temp = l[j].split()
        if(int(temp[0])>max_activity_id):
            max_activity_id = int(temp[0])

    if(max_activity_id == 0):
        response = ERRO + "nao existem atividades"
        return response

    for j in range(len(l)):                                     #vai buscar dados da atividade em questao
        temp = l[j].split()
        if(temp[0] == req[1]):
            lot_temp = int(temp[4])
            prof_temp = temp[3]
            dur_temp = temp[5]
    
    f = open("clients.txt", "r")
    l = f.readlines()
    f.close()

    for j in range(len(l)):                                     
        temp = l[j].split()
        if(int(temp[0]) == int(req[2])):
            if(prof_temp != temp[3]):                           #se o utente tiver uma profissao nao adequada ha atividade entao
                response = ERRO + PED_AT_ERR_1                  #nap a podera realizar
                return response 

    if(activity_tracker[int(req[1])][0] == lot_temp):           #verifica se a lotacao para a atividade esta cheia
        response = ERRO + PED_AT_ERR_2
        return response

    activity_tracker[int(req[1])][0] += 1                       
    for j in range(len(activity_tracker[int(req[1])])):         
        if(activity_tracker[int(req[1])][j] == 0):              #adiciona o id do utente ao array activity_tracker na primeira
            activity_tracker[int(req[1])][j] = int(req[2])      #livre
            break

    for j in range(len(l)):                                     #esta seccao serve para reescrever o client.txt mas com o cliente               
        temp = l[j].split()                                     #que entrou numa atividade com um 1 no fim
        if(int(temp[0]) == int(req[2])):     
            line_temp[0] = temp[0]
            line_temp[1] = temp[1]
            line_temp[2] = temp[2]
            line_temp[3] = temp[3]
            line_temp[4] = temp[4]
            line_temp[5] = temp[5]
            line_temp[6] = temp[6]
            line_temp[7] = "1"
            x = j
    del l[x]

    new_f = open("clients.txt", "w+")

    for line in l:
        new_f.write(line)
    new_f.close()   

    f_2 = open("clients.txt", "a")
    f_2.write(line_temp[0]+" "+line_temp[1]+" "+line_temp[2]+" "+line_temp[3]+" "+line_temp[4]+" "+line_temp[5]+" "+line_temp[6]+" "+line_temp[7]+"\n")
    f_2.close()

    response ="ATIVIDADE: " +str(req[1]) + " DURACAO: " + dur_temp

    return response

def complain(request):
    response = ""
    req = request.split(" ",3)
    id_L = 0
    max_id_R = 0

    if(len(req) != 4):
        response = ERRO + RCL_ERR_1
        return response
            
    try:
        i = int(req[1])
    except ValueError:
        return ERRO + RCL_ERR_1
    
    if(not int_veracity(int(req[1]))):
        response = ERRO + RCL_ERR_1
        return response
    elif(not str_veracity(req[2])):
        response = ERRO + RCL_ERR_1
        return response
    elif(not str_veracity(req[3])):
        response = ERRO + RCL_ERR_1
        return response

    f = open("locals.txt", "r")
    l = f.readlines()
    f.close()

    for j in range(len(l)):           #encontra o id da localizacao se existir
        temp = l[j].split()
        if(int(temp[0]) == int(req[1])):
            id_L = int(temp[0])
    
    if(id_L == 0):                    #caso nao exista da erro
        response = ERRO + RCL_ERR_2
        return response

    f = open("complaints.txt", "r")
    l = f.readlines()
    f.close()
    
    for j in range(len(l)):           #encontra o id de reclamacao mais alto criado ate ao momento
        temp = l[j].split()
        if(int(temp[0])>max_id_R):
            max_id_R = int(temp[0])

    max_id_R += 1 

    f = open("complaints.txt", "a")             #adiciona a nova reclamacao
    f.write(str(max_id_R)+" "+req[1]+" "+req[2]+" "+req[3])
    f.close()

    response = "id_R:" + str(max_id_R)
    
    return response

def manager(request):                           #decide o que fazer com a menssagem do cliente
    temp = request.split()
    
    if(temp[0] == "REGISTAR_CLIENTE"):
        request = register_client(temp)
        return request
    if(temp[0] == "MODIFICAR_PERFIL"):
        request = update_client(temp)
        return request
    if(temp[0] == "REMOCAO_UTENTE"):
        request = remove_client(temp)
        return request
    if(temp[0] == "CONSULTAR_ATIVIDADES"):
        request = check_activities(temp)
        return request
    if(temp[0] == "PEDIR_ATIVIDADES"):
        request = request_activity(temp)
        return request
    if(temp[0] == "RECLAMAR"):
        request = complain(request)
        return request
     
    request = ERRO + ERR_REQ

    return request



def handle_client_connection(client_socket):
    try:
        with rlock:                                           #garante que uma pessoa nao esta a ler e a escrever ao mesmo tempo
            client_sockets.append(client_socket)              #junta o client_socket ao array de client_sockets que pode ir ate 5 ao mesmo tempo
        while True:
            rcv_message = ""
            while(rcv_message == "" or rcv_message[-1] != '\n'):        #enquanto a mensagem nao existir ou nao chegar ao fim da mensagem
                msg_from_client = client_socket.recv(buffer)            
                if(not msg_from_client):                                #se nao for recebida nenhuma mensagem o cliente e desconectado
                    raise socket.timeout()                              #mais em baixo
                rcv_message += str(msg_from_client.decode())            
                msg_to_client = manager(rcv_message)                    #vai fazer manage da mensagem em que fez decode
                #print(msg_to_client)
                with rlock:
                    client_socket.send(msg_to_client.encode())          #envia a mensagem de volta para o respetivo cliente 
    except socket.timeout:
        with rlock:
            for i in range(len(client_sockets)):                #apaga o client_socket que se desconectou
                if(client_sockets[i]==client_socket):       
                    del(client_sockets[i])
                    break
        client_socket.close()
        print("Client offline {} ".format(client_socket))
        exit(0)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((bind_ip, bind_port))
    server.listen(5)  # max backlog of connections
    print ('Listening on {}:{}'.format(bind_ip, bind_port))
    
    while True:
        client_sock, address = server.accept()
        print ('Accepted connection from {}:{}'.format(address[0], address[1]))
        client_handler = threading.Thread(target=handle_client_connection, args=(client_sock, ))  # without comma you'd get a... TypeError: handle_client_connection() argument after * must be a sequence, not _socketobject
        client_handler.start()

if(__name__ == '__main__'):
    main()