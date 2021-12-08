import socket
import threading
import argparse
import os
import time
import sys
import subprocess
import pyqrcode
import pkg_resources
from datetime import datetime

required = {'pyqrcode', 'tqdm'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing_package = required - installed

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for package in missing_package:
    install(package)

parser = argparse.ArgumentParser(description='This is server!\n')
# parser.add_argument('!req',help=' Request file from server\n')
args = parser.parse_args()

HOST = '192.168.0.18'
PORT = 12002
FORMAT = 'utf-8'
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ADDRESS = (HOST,PORT)
ASK_NAME = 'Please enter your name : '
server.bind(ADDRESS)
server.listen()
QUIT_CLIENT_MESSAGE = '!exit'
REQUEST_FILE = '!req'
COMMAND = '!cmd'
HEADER = 1000*1000*1024
SEPARATOR = '<>'
clients = []
names = []
BANK_AUTHENTICATION = '!get'
SERVER_NAME = 'server.py'
CLIENT_NAME = 'client.py'
QR_CODE = 'qr'
ONLINE_CLIENTS = '!online'

def broadcast_message(message,flag_client=None):
    for client in clients:
        if client != flag_client:
            client.send(message)

def remove_client(client):
    index = clients.index(client)
    clients.remove(client)
    name_to_remove = names[index]
    names.remove(name_to_remove)
    print(f'**Client leaving** {name_to_remove} is leaving the chat')
    broadcast_message(f'{name_to_remove} had left the chat!'.encode(FORMAT))
    client.close()
    print(f'Active connections at {str(datetime.now())} : ',len(clients))

def handle_client(client,address):
    print(f'[New connection] Address with {address} connected!')
    print(f'Active connections at {str(datetime.now())} : ',len(clients))
    while True:
        try:
            message = client.recv(HEADER)
            msg = message.decode(FORMAT)
            if QUIT_CLIENT_MESSAGE in msg:
                break

            elif ONLINE_CLIENTS in msg:
                names_online = '\n'.join(names)
                msg = 'Currently online : \n'+names_online+'\n'+10*"*="+'*'
                client.send(msg.encode(FORMAT))

            elif REQUEST_FILE in msg:
                try:
                    file_name = msg.split(' ')[-1].strip()
                    client_name = msg.split(' ')[0].strip()
                    print(f'{client_name} requested file with name : {file_name}')
                    file_size = os.path.getsize(file_name)
                    client.send(f'{file_name}{SEPARATOR}{file_size}'.encode(FORMAT))
                    file = open(file_name,'rb')
                    bytes_size = 0
                    contents = 0
                    while bytes_size < file_size:
                        contents = file.read(1024)
                        if not contents:
                            break
                        bytes_size += len(contents)
                        client.send(contents)
                    file.close()
                    print('File sent successfully')
                except:
                    print('Unable to find/open the file')
                    client.send('Unable to find/open the file'.encode(FORMAT))

            elif COMMAND in msg:
                try:
                    command = msg.split(':')[-1].split(COMMAND)[-1].strip()
                    if 'rm' in command or 'sudo' in command:
                        raise Exception
                    print('Command to execute : ',command)
                    print('Command executed and sending output')
                    msg = f'[**Executing**] $ {command} : \n'
                    result = subprocess.check_output(command).decode(FORMAT)
                    if 'ls' in command:
                        result = result.split('\n')
                        result.remove(CLIENT_NAME)
                        result.remove(SERVER_NAME)
                        result = '\n'.join(result)
                    result = msg + result + 10*"*="+'*'
                    client.send(result.encode(FORMAT))
                except:
                    msg = f'No previliges to run the command:{command}'
                    print(msg)
                    msg = '[**Warning**] '+msg
                    client.send(msg.encode(FORMAT))

            elif BANK_AUTHENTICATION in msg:
                try:
                    bank_url = 'www.myCNbank.org'
                    url = pyqrcode.create(bank_url)
                    file_name = 'bank_request.png'
                    url.png(file_name,scale=10)
                    file_size = os.path.getsize(file_name)
                    client.send(f'{file_name}{SEPARATOR}{file_size}{SEPARATOR}{QR_CODE}'.encode(FORMAT))
                    file = open(file_name,'rb')
                    bytes_size = 0
                    contents = 0
                    while bytes_size < file_size:
                        contents = file.read(1024)
                        if not contents:
                            break
                        bytes_size += len(contents)
                        client.send(contents)
                    file.close()
                    print('QR sent successfully')
                    os.remove(file_name)
                except:
                    print('Error in creating QR code')

            else:
                broadcast_message(message,client)
        except:
            pass
            
    remove_client(client)
    
def recieve_from_client():
    print(f'**Starting** Starting the server')
    print(f'Server listening at {HOST}')

    try:
        while True:
            client,address = server.accept()
            
            client.send(ASK_NAME.encode(FORMAT))
            new_name = client.recv(HEADER).decode(FORMAT)
            names.append(new_name)
            clients.append(client)
            
            print(f'**Connecting** Client connecting with name : {new_name}')
                    
            client.send('connected to server!'.encode(FORMAT))
            broadcast_message(f'{new_name} has joined the chat!'.encode(FORMAT))
            
            thread = threading.Thread(target=handle_client,args=(client,address))
            thread.start()
            
    except KeyboardInterrupt:
        print('**[Terminating]** Server terminating')
        while(len(clients)):
            clients[0].send(QUIT_CLIENT_MESSAGE.encode(FORMAT))
            time.sleep(0.1)
            remove_client(clients[0])
        server.shutdown(socket.SHUT_RDWR)
        server.close()
        print ("Server terminated!")
        os._exit(0)

recieve_from_client()