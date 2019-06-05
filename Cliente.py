# UNIVERSIDADE FEDERAL DO RIO GRANDE DO NORTE
# DEPARTAMENTO DE ENGENHARIA DE COMPUTACAO E AUTOMACAO
# DISCIPLINA REDES DE COMPUTADORES (DCA0113)
# AUTORES: Francisco Kennedi
#          Lara Beatriz
# SCRIPT: Chat com servidor (Cliente)
#

# importacao das bibliotecas
from socket import *
from threading import Thread
import pickle


class Commands:
    PUBLIC = 0
    PRIVATE = 1
    NAME = 2
    LIST = 3
    EXIT = 4
    QUITPVD = 5


class Client(Thread):
    def __init__(self, nickname, ip_server='localhost', port=65000):
        Thread.__init__(self)

        self.nickname = nickname
        if self.validator_nickname(nickname) is False:
            raise Exception("Nickname deve possuir até 8 caracteres e ser diferente de string vazia")

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.ip_server = ip_server
        self.port = port
        self.len_message = None
        self.command = -1
        self.message = ''
        self.online = True

    def run(self):
        try:
            self.client_socket.connect((self.ip_server, self.port))
        except:
            print("Falha ao manter comunicação com o servidor")
            self.exit_connection()
            exit()

        self.client_socket.send(self.nickname.encode('utf-8'))
        while self.online is True:
            self.receive_message()
        exit()

    def send_message(self):
        self.message = input()
        self.command, arg = self.select_command(self.message)
        header_server = self.header(self.nickname, self.command, arg)
        # header_encode = {k: v.encode("utf-8") for k,v in header_server}
        self.client_socket.send(pickle.dumps(header_server))
        if self.command == Commands.EXIT:
            self.exit_connection()

    def receive_message(self):
        while self.command != Commands.EXIT:
            message_server = self.client_socket.recv(1024)
            if not message_server:
                break
            print(message_server.decode())
        self.exit_connection()

    def keep_online(self):
        return self.online

    def validator_nickname(self, nickname):
        if nickname is '':
            return False
        elif len(nickname) > 8:  # garantindo que o nickname terá no máximo 8 octetos
            self.nickname = nickname[:8]
        return True

    @staticmethod
    def select_command(message):
        comando = Commands.PUBLIC  # por padrão a conexao do chat é pública e espera-se que o usuario digitou uma mensagem

        if message.find('(') is -1:  # caso não seja encontrado parentese na string, é apenas uma mensagem normal
            return comando, message
        elif message.find(
                ')') is -1:  # caso seja encontrado um parentese, mas nao o seu fechamento, é também uma mensagem
            return comando, message

        split_string = message.split('(')
        comando = split_string[0]
        arg = split_string[1].split(')')[0]

        if comando == 'listar':
            comando = Commands.LIST
        elif comando == 'sair':
            comando = Commands.EXIT
        elif comando == 'nome':
            comando = Commands.NAME
        elif comando == 'privado':
            comando = Commands.PRIVATE
        elif comando == 'quitpvd':
            comando = Commands.QUITPVD
        else:
            print("Comando não encontrado")
            exit()

        return comando, arg

    @staticmethod
    def header(name, command, data):
        if len(data) > 80: # caso a mensagem possua mais do que 80 caracteres (octetos), deverá ser truncada
            data = data[:80]

        size_header = len(data) + 4 + len(name)

        if size_header > 99:
            print("Tamanho da mensagem maior do que o permitido")

        dict_header = {
            "size": size_header,
            "nickname": name,
            "command": command,
            "data": data
        }

        return dict_header

    def exit_connection(self):
        self.client_socket.close()
        self.online = False


# definicao das variaveis
serverName = 'localhost'
serverPort = 65000  # porta a se conectar
message = ''
nickname = input('Digite o seu nome: ')
print('Bem vindo, pode começar a conversar!\n')

cliente = Client(nickname=nickname, ip_server=serverName, port=serverPort)
cliente.start()

while cliente.keep_online() is True:
    cliente.send_message()
print("Bye")
