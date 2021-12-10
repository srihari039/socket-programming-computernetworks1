# CS 3530 : Computer Networks - I

## Socket Programming Assignment
## Multi-Media Group Chat
======================================

Commands to run the program :

* ```$ python3 server.py``` 
* ```$ python3 client.py```

On running "client.py" file the user is prompted to : 

- *Enter the IP address :*
- *Enter the port Number :*
- *Please enter your name :* 

On choosing the suitable HOST and PORT, the client is connected to the server and displays :
- *connected to server!*
- *"client_name" has joined the chat!*

<<<<<<< HEAD
This gives a confirmation that a client connected to a server.

=======
>>>>>>> 81162053d41d9cd63faa7f8e9f6a0d3eb727ccb0
### BASE LINE IMPLEMENTATION
#### Normal Text Chat

- To text in the group chat with other clients type the message and then click enter. 
<<<<<<< HEAD
- Used normal ```send,recv``` functions to send and recieve data.
=======

>>>>>>> 81162053d41d9cd63faa7f8e9f6a0d3eb727ccb0

### ENHANCED VERSION

#### OS Commands
- ``` !cmd "Linux Commands"``` command is used to execute the OS commands. 
<<<<<<< HEAD
- It supports all the basic linux commands like *ls, date, echo.*
=======
- It supports all the basic linux commands like *ls, date, time.*
>>>>>>> 81162053d41d9cd63faa7f8e9f6a0d3eb727ccb0
- The commands ```sudo, rm, rf``` are not supported and are considered as error commands.
- For example, ```!cmd ls``` command outputs the list of all the files in the present directory.


<<<<<<< HEAD
### File Transfer
- ```!send "filename"``` command is used to send a file from the client to the server.
- ```!req "filename"``` command is used to request a file from the server to the client.
- It supports all file extensions like ```.txt, .pdf, .mp3, .mp4, .jpeg, .png, .py....```
- Divided file into fine chunks and then transferred properly.

### Bank Authentication
- ```!get "QR Code"``` pops out the unique generated QR Code for a given URL.
- The recieved Qr code will be automatically deleted within 5 seconds.

### Pre-installations to run the files
- Apart from normal packages, ```tqdm``` and ```pyqrcode``` packages are to be installed.
- We added support to add missing packages using pkg_resources, subprocess module in python.
=======
### Flie Transfer
- ```!send "filename"``` command is used to send a file from the client to the server.
- ```!req "filename"``` command is used to request a file from the server to the client.
- It supports all file extensions like ```.txt, .pdf, .mp3, .mp4, .jpeg, .png, .py....```

### Bank Authentication
- ```!get "QR Code"``` pops out the unique generated QR Code for a given URL.

### Pre-installations to run the files
- Missing packages are installed using subprocessed module in python automatically.
>>>>>>> 81162053d41d9cd63faa7f8e9f6a0d3eb727ccb0
