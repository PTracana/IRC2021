import socket, signal, sys, select, os

server_ip = [socket.gethostbyname("pedro.freetcp.com"), "127.0.0.1"]
server_port = 9993
server = -1
MSG_SIZE = 1024

VLINE=chr(9474)
username=''

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