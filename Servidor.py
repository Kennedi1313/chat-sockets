# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# DISCIPLINA REDES DE COMPUTADORES (DCA0113)
# AUTORES: Francisco Kennedi
#          Lara Beatriz
# SCRIPT: Chat com servidor (Servidor)
#

# importacao das bibliotecas
from socket import *  # sockets
import threading
import pickle

dict_nickname = dict()
dict_ip_nickname = dict()
privateList = []


class Commands:
    PUBLIC = 0
    PRIVATE = 1
    NAME = 2
    LIST = 3
    EXIT = 4
    QUITPVD = 5


def on_client(key, nickname):
    information_on_client = nickname.decode('utf-8') + ' entrou na sala'
    dict_nickname[key] = nickname.decode('utf-8')
    return information_on_client


def out_client(key, nickname):
    dict_nickname.pop(key, nickname)
    information_client_out = nickname + " saiu."
    for client in dict_nickname:
        if client != key:
            client.send(information_client_out.encode('utf-8'))
    return information_client_out


def change_nick(key, nickname):
    current_name = dict_nickname[key]
    dict_nickname[key] = nickname
    return current_name + " alterou o nome para " + nickname


def client_says(key, message):
    if message != 'quit':
        return dict_nickname[key] + ': ' + message


def client_list(addr):
    string = 'Os clientes conectados são: \n'
    for client in dict_nickname:
        string += '[<' + dict_nickname[client] + '> <' + str(addr[0]) + '> <' + str(addr[1]) + '>] \n'
    return string


def exit_connection(conn):
    client_disconnect = out_client(conn, dict_nickname[conn])
    write_file(client_disconnect)
    print(client_disconnect)


def send_broadcast(conn, message):
    for client in dict_nickname:
        if client != conn:
            client.send(message)


def write_file(message):
    f = open('historico.txt', 'a')
    f.write(message + '\n')
    f.close()


def send_history(conn):
    f = open('historico.txt', 'r')
    historico = f.read()
    conn.send(historico.encode('utf-8'))
    f.close()


def inPrivate(conn):
    for linha in privateList:
        for client in linha:
            if conn == client:
                return True
    return False


def connect_client(conn, addr):

    # Entrada do cliente no chat
    nickname = conn.recv(1024)
    print(on_client(conn, nickname))
    send_broadcast(conn, on_client(conn, nickname).encode('utf-8'))
    write_file(on_client(conn, nickname))

    # Validacao do comando recebido
    message = {'command': '', 'data': ''}
    while message['command'] != Commands.EXIT:
        message = conn.recv(1024)  # recebe dados do cliente
        message = pickle.loads(message)
        if not message:
            break
        command = message['command']
        content = message['data']
        if command == Commands.LIST:
            conn.send(client_list(addr).encode('utf-8'))

        elif command == Commands.NAME:
            nick_changed = change_nick(conn, content)
            print(nick_changed)
            write_file(nick_changed)
            send_broadcast(conn, nick_changed.encode('utf-8'))

        elif command == Commands.PRIVATE:
            destination_user = content
            client_pvd = None
            for client in dict_nickname:
                if dict_nickname[client] == destination_user:
                    client_pvd = client
                    string = dict_nickname[conn] + ' iniciou um privado. Digite "s" para aceitar e "n" para sair'
                    client_pvd.send(string.encode('utf-8'))
                    break
            confirmation = {'command': '', 'data': ''}
            confirmation = client_pvd.recv(1024)
            confirmation = pickle.loads(confirmation)
            confirmation = confirmation['data']
            if confirmation == 's':
                print('Privado iniciado')
                conn.send('Privado iniciado'.encode('utf-8'))
                client_pvd.send('Privado iniciado'.encode('utf-8'))
                privateList.append([conn, client_pvd])
                # privateList.append(client_pvd)
            else:
                print('Privado recusado')
                conn.send('Privado recusado'.encode('utf-8'))
                client_pvd.send('Privado recusado'.encode('utf-8'))

        elif command == Commands.QUITPVD:
            client_pvd = None
            index = 0
            for linha in privateList:
                if conn == linha[0]:
                    client_pvd = linha[1]
                    break
                elif conn == linha[1]:
                    client_pvd = linha[0]
                    break
                index += 1

            if inPrivate(client_pvd):
                conn.send('Privado encerrado'.encode('utf-8'))
                client_pvd.send('Privado encerrado'.encode('utf-8'))

            privateList.pop(index)

        elif inPrivate(conn):
            client_pvd = None
            for linha in privateList:
                if conn == linha[0]:
                    client_pvd = linha[1]
                    break
                elif conn == linha[1]:
                    client_pvd = linha[0]
                    break
            client_pvd.send(content.encode('utf-8'))

        else:
            if client_says(conn, content) is not None:
                message_all = client_says(conn, content)
                print(message_all)
                write_file(message_all)
                send_broadcast(conn, message_all.encode('utf-8'))

    exit_connection(conn)


def listener_clients():

    while True:
        conn, addr = serverSocket.accept() #aceita as conexões dos clientes
        threading.Thread(target=connect_client, args=(conn, addr,)).start()

    serverSocket.close() # encerra o socket do servidor

"""
Configurando o servidor
"""
serverName = ''  # ip do servidor (em branco)
serverPort = 65000  # porta a se conectar
serverSocket = socket(AF_INET, SOCK_STREAM)  # criacao do socket TCP
serverSocket.bind((serverName, serverPort))  # bind do ip do servidor com a porta
serverSocket.listen(1)  # socket pronto para 'ouvir' conexoes
print('Servidor TCP esperando conexoes na porta %d ...' % serverPort)
file = open('historico.txt', 'w')
file.write('')
file.close()
listener_clients()  # Chama função para escutar os clientes

# while 1:
#     connectionSocket, addr = serverSocket.accept()  # aceita as conexoes dos clientes
#     message = connectionSocket.recv(1024)  # recebe dados do cliente
#     print(connectionSocket.fileno())
#     print(on_client(addr, message))
#     print(dict_nickname)
#     while message != 'quit':
#         print('Cliente %s enviou: %s' % (addr, message))
#         message = connectionSocket.recv(1024)
#         if not message:
#             break
#         connectionSocket.send(message)  # envia para o cliente o texto transformado
#         # print("Lista de clientes conectados: ", str(lista_addr))

