import socket
import threading
import os
import argparse
import time
import pkg_resources
import subprocess
import sys
from tqdm import tqdm
from PIL import Image

required = {'pyqrcode', 'tqdm'}
installed = {pkg.key for pkg in pkg_resources.working_set}
missing_package = required - installed

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for package in missing_package:
    install(package)

parser = argparse.ArgumentParser(description='This is client')
args = parser.parse_args()

HOST = '192.168.0.18'
# HOST = '127.0.0.1'
PORT = 12002
FORMAT = 'utf-8'
ADDRESS = (HOST,PORT)
ASK_NAME = 'Please enter your name : '
HEADER = 1000*1024*1000
CLIENT_NAME = input(ASK_NAME)
MAX_COUNT = 1e5
REQUEST_FILE = '!req'
QUIT_CLIENT_MESSAGE = '!exit'
SEPARATOR = '<>'
QR_CODE = 'qr'
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
client.connect(ADDRESS)

def split_get(message):
    file_name = message.split(SEPARATOR)[0]
    file_size = int(message.split(SEPARATOR)[1])
    one,two = file_name.split('.')
    file_name = one+'_recieved.'+two
    return file_name,file_size
    
def recieve_from_server():
    count = 0
    while True:
        try:
            message = client.recv(HEADER)
            message = message.decode(FORMAT)
            if message == ASK_NAME:
                client.send(CLIENT_NAME.encode(FORMAT))
            elif message == QUIT_CLIENT_MESSAGE:
                print('[**Terminating**] Terminating connection from server side')
                print('Connection removed!')
                os._exit(0)
            elif message == '':
                count += 1
            elif QR_CODE in message:
                file_name,file_size = split_get(message)
                file = open(file_name,'wb')
                bytes_size = 0
                while bytes_size < file_size:
                    contents = client.recv(1024)
                    bytes_size += len(contents)
                    file.write(contents)
                file.close()
                img = Image.open(file_name)
                img.show()
                client.send(QR_CODE.encode(FORMAT))
                
                thread = threading.Thread()
                thread.start()
                time.sleep(2)
                print('Closing the qr code')
                os.remove(file_name)
            
            elif SEPARATOR in message:
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
                
                print(f'File name with {file_name} recieved successfully')

            else:
                print(message)

            if count > MAX_COUNT:
                raise Exception

        except:
            pass


def write_to_server():
    while True:
        msg = input('')
        message = f'{CLIENT_NAME} : {msg}'.encode(FORMAT)
        original_message = message.decode(FORMAT)
        client.send(message)

        if original_message == f'{CLIENT_NAME} : !exit':
            os._exit(0)
        
recieve_thread = threading.Thread(target=recieve_from_server)
recieve_thread.start()

write_to_server()