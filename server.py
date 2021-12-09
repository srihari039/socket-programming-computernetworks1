# importing useful libraries
import socket
import threading
import os
import argparse
import time
import sys
import pkg_resources
import subprocess
import pyqrcode
from tqdm import tqdm
from datetime import datetime

# these are the libraries generally not installed in all the laptops
# check and install if these libraries are not present
required = {'pyqrcode', 'tqdm'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing_package = required - installed

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for package in missing_package:
    install(package)

# argument parser
parser = argparse.ArgumentParser(description='This is server!\n')
args = parser.parse_args()

# Host and port
HOST = '192.168.0.18'
PORT = 12002

# creating server and binding address to listen
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
ADDRESS = (HOST,PORT)
server.bind(ADDRESS)

# listen on server
server.listen()

# global attributes / key Identifiers
FORMAT = 'utf-8'
ASK_NAME = 'Please enter your name : '
QUIT_CLIENT_MESSAGE = '!exit'
REQUEST_FILE = '!req'
SEND_FILE = '!send'
COMMAND = '!cmd'
HEADER = 100*1024
SEPARATOR = '<>'
clients = []
names = []
BANK_AUTHENTICATION = '!get'
SERVER_NAME = 'server.py'
CLIENT_NAME = 'client.py'
QR_CODE = 'qr'
ONLINE_CLIENTS = '!online'

# function to broadcast message
# sends a particluar message to all clients
# except the client from whom the message comes
def broadcast_message(message,flag_client=None):
    for client in clients:
        if client != flag_client:
            client.send(message)

# function to remove client from server
# closes the client connection 
def remove_client(client):
    index = clients.index(client)
    clients.remove(client)
    name_to_remove = names[index]
    names.remove(name_to_remove)
    print(f'**Client leaving** {name_to_remove} is leaving the chat')
    broadcast_message(f'{name_to_remove} had left the chat!'.encode(FORMAT))
    client.close()
    print(f'Active connections at {str(datetime.now())} : ',len(clients))

# utility function to split messages
def split_get(message):
    file_name = message.split(SEPARATOR)[0]
    file_size = int(message.split(SEPARATOR)[1])
    one,two = file_name.split('.')
    file_name = one+'_recieved_to_server.'+two
    return file_name,file_size    

# function to send files to client
def send_file(file_name,file_size,client):
    # open the file with read bytes mode
    file = open(file_name,'rb')
    bytes_size = 0
    contents = 0
    # read chunks at time and send each one individually
    with tqdm(total=file_size) as progress_bar:
        while bytes_size < file_size:
            contents = file.read(1024)
            if not contents:
                break
            progress_bar.update(len(contents))
            bytes_size += len(contents)
            client.send(contents)
    # close the file
    file.close() 

# function which handles the client
def handle_client(client,address):
    print(f'[New connection] Address with {address} connected!')
    print(f'Active connections at {str(datetime.now())} : ',len(clients))
    
    while True:
        try:
            # server tries to recieve message
            message = client.recv(HEADER)
            msg = message.decode(FORMAT)
            
            # if quit message appears, break and remove the client
            if QUIT_CLIENT_MESSAGE in msg:
                break

            # if online clients appears in message, lists names of clients online
            elif ONLINE_CLIENTS in msg:
                names_online = '\n'.join(names)
                msg = 'Currently online : \n'+names_online+'\n'+10*"*="+'*'
                client.send(msg.encode(FORMAT))
    
            # if send request from client, then deal accordingly
            # by writing byte format to files
            elif SEND_FILE in msg:
                message = client.recv(HEADER).decode(FORMAT)
                file_name,file_size = split_get(message)
                print(f'File incoming with name {file_name}')
                
                file = open(file_name,'wb')
                bytes_size = 0
                while bytes_size < file_size:
                    contents = client.recv(1024)
                    bytes_size += len(contents)
                    file.write(contents)
                file.close()
                print('File recived from client')

            # if request file from client, then deal accodingly
            # by reading and sending to client
            elif REQUEST_FILE in msg:
                try:
                    file_name = msg.split(' ')[-1].strip()
                    client_name = msg.split(' ')[0].strip()
                    print(f'{client_name} requested file with name : {file_name}')
                    file_size = os.path.getsize(file_name)
                    client.send(f'{file_name}{SEPARATOR}{file_size}'.encode(FORMAT))
                    send_file(file_name,file_size,client)
                    print('File sent successfully')
                except:
                    print('Unable to find/open the file')
                    client.send('Unable to find/open the file'.encode(FORMAT))

            # if command is requested by client, then deal accordingly
            # by giving access properly only to certain commands
            elif COMMAND in msg:
                try:
                    command = msg.split(':')[-1].split(COMMAND)[-1].strip()
                    if 'rm' in command or 'sudo' in command:
                        raise Exception
                    print('Command to execute : ',command)
                    print('Command executed and sending output')
                    msg = f'[**Executing**] $ {command} : \n'
                    result = subprocess.check_output(command, shell=True).decode(FORMAT)
                    if 'ls' in command:
                        result = result.split('\n')
                        result.remove(CLIENT_NAME)
                        result.remove(SERVER_NAME)
                        result = '\n'.join(result)
                    result = msg + result + '\n'
                    client.send(result.encode(FORMAT))
                except:
                    msg = f'No previliges to run the command:{command}'
                    print(msg)
                    msg = '[**Warning**] '+msg
                    client.send(msg.encode(FORMAT))

            # if client requests for bank authentication, then
            # send the qr code file
            elif BANK_AUTHENTICATION in msg:
                try:
                    bank_url = 'www.myCNbank.org'
                    url = pyqrcode.create(bank_url)
                    file_name = 'bank_request.png'
                    url.png(file_name,scale=10)
                    file_size = os.path.getsize(file_name)
                    client.send(f'{file_name}{SEPARATOR}{file_size}{SEPARATOR}{QR_CODE}'.encode(FORMAT))
                    send_file(file_name,file_size,client)
                    print('QR sent successfully')
                    os.remove(file_name)
                except:
                    print('Error in creating QR code')

            else:
                broadcast_message(message,client)
        except:
            pass
            
    remove_client(client)
    
# function which deals with all clients
# establishes a server and connects clients upon request
def recieve_from_client():
    print(f'**Starting** Starting the server')
    print(f'Server listening at {HOST}')

    try:
        while True:
            # accepting request from client
            client,address = server.accept()
            print('New connection request incoming!')
            
            # recording the name of the client
            client.send(ASK_NAME.encode(FORMAT))
            new_name = client.recv(HEADER).decode(FORMAT)
            
            # keep the name and clients in a list
            # to access them further for utility
            names.append(new_name)
            clients.append(client)
            
            print(f'**Connecting** Client connecting with name : {new_name}')
            
            client.send('connected to server!\n'.encode(FORMAT))
            broadcast_message(f'{new_name} has joined the chat!'.encode(FORMAT))
            
            # starting a new thread and assigning it to new client
            thread = threading.Thread(target=handle_client,args=(client,address))
            thread.start()
            
    # keyboard interrupt exception
    except KeyboardInterrupt:
        print('**[Terminating]** Server terminating')
        
        # remove all clients one by one
        while(len(clients)):
            clients[0].send(QUIT_CLIENT_MESSAGE.encode(FORMAT))
            time.sleep(0.1)
            remove_client(clients[0])
        
        # shutdown the server and close
        server.shutdown(socket.SHUT_RDWR)
        server.close()
        print ("Server terminated!")
        # exit the program
        os._exit(0)

recieve_from_client()