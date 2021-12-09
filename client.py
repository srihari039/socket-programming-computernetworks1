# importing useful libraries
import socket
import threading
import os
import argparse
import time
import sys
import pkg_resources
import subprocess
from tqdm import tqdm
from PIL import Image

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
parser = argparse.ArgumentParser(description='This is client')
args = parser.parse_args()

# Host and Port
HOST = input('Enter the IP address : ')
PORT = int(input('Enter the port Number : '))
ADDRESS = (HOST,PORT)

# create a client and connect with server
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(ADDRESS)

# global attributes / key Identifiers
FORMAT = 'utf-8'
ASK_NAME = 'Please enter your name : '
HEADER = 100*1024
CLIENT_NAME = input(ASK_NAME)
MAX_COUNT = 1e5
REQUEST_FILE = '!req'
QUIT_CLIENT_MESSAGE = '!exit'
SEND_FILE = '!send'
SEPARATOR = '<>'
QR_CODE = 'qr'

# utility function to split the name and get attributes from the message
def split_get(message):
    file_name = message.split(SEPARATOR)[0]
    file_size = int(message.split(SEPARATOR)[1])
    one,two = file_name.split('.')
    file_name = one+'_recieved.'+two
    return file_name,file_size

# function to recieve file from server
def recieve_file(message):
    file_name,file_size = split_get(message)
    print(file_name,file_size)
    file = open(file_name,'wb')
    bytes_size = 0
    with tqdm(total=file_size) as progress_bar:
        while bytes_size < file_size:
            contents = client.recv(1024)
            bytes_size += len(contents)
            progress_bar.update(len(contents))
            file.write(contents)
        file.close()
    # returning file name for further flow
    return file_name

# function which listens/recieves to server
def recieve_from_server():
    count = 0
    while True:
        try:
            # recieve message from server
            message = client.recv(HEADER)
            message = message.decode(FORMAT)
            
            # if it asks name, send the name
            if message == ASK_NAME:
                client.send(CLIENT_NAME.encode(FORMAT))
                
            # if message is to quit, then quit the connection
            elif message == QUIT_CLIENT_MESSAGE:
                print('[**Terminating**] Terminating connection from server side')
                print('Connection removed!')
                os._exit(0)
            
            # elif block  with no use--> to be commented
            elif message == '':
                count += 1
                
            # if qr in message, deal accordingly to recieve the file
            elif QR_CODE in message:
                file_name = recieve_file(message)
                print(f'QR code recieved successfully')
                img = Image.open(file_name)
                img.show()
                client.send(QR_CODE.encode(FORMAT))

                # starting a thread
                # a qr must be safe and expire after some time,
                # so deleting the file after 5 seconds 
                thread = threading.Thread()
                thread.start()
                time.sleep(5)
                print('Closing the qr code')
                os.remove(file_name)
            
            # if client to recieve message, use the utility function
            # and recieve the file
            elif SEPARATOR in message:
                file_name = recieve_file(message)
                print(f'File name with {file_name} recieved successfully')
                
            # else print the message
            else:
                print(message)

            # to be commented block
            if count > MAX_COUNT:
                raise Exception

        except:
            pass

# function which writes to the server
def write_to_server():
    while True:
        try:
            # take the input and send the message
            msg = input('')
            message = f'{CLIENT_NAME} : {msg}'.encode(FORMAT)
            original_message = message.decode(FORMAT)
            client.send(message)

            # if a file is to be sent to server
            if SEND_FILE in original_message:
                try:
                    # read and send file dividing into fine chunks
                    file_name = msg.split(' ')[-1]
                    file_size = os.path.getsize(file_name)
                    print(f'Sending {file_name} to server')
                    client.send(f'{file_name}{SEPARATOR}{file_size}'.encode(FORMAT))
                    time.sleep(0.1)
                    file = open(file_name,'rb')
                    bytes_size = 0
                    contents = 0
                    with tqdm(total=file_size) as progress_bar:
                        while bytes_size < file_size:
                            contents = file.read(1024)
                            if not contents:
                                break
                            bytes_size += len(contents)
                            progress_bar.update(len(contents))
                            client.send(contents)
                        file.close()
                    print('File sent successfully')
                except:
                    print('Unable to open/read file')

            # if message is to exit, then exit from the program
            if original_message == f'{CLIENT_NAME} : !exit':
                os._exit(0)
        
        # exception for keyboard interrupt
        except KeyboardInterrupt:
            # send message to server, to remove the connection
            message = f'{CLIENT_NAME} : !exit'.encode(FORMAT)
            client.send(message)
            # exit the program
            print('[**Key board interrupt**] Terminating connection')
            os._exit(0)
        
# we need to run "recieve_from_server" and "write_to_server" simultaneously
# it is achieved using threads

# thread to start function which recieves responses from server
recieve_thread = threading.Thread(target=recieve_from_server)
recieve_thread.start()

# function write to server
write_to_server()