import sys

import socket

serverIP = '127.0.0.1'
# Creates socket for active connection to server
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("Attempting to connect to server...")
serverSocket.connect((serverIP, 5000))
print("Connected to server.")

rendererIP = '127.0.0.1'
# Creates socket for active connection to renderer
rendererSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
rendererSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("Attempting to connect to renderer...")
rendererSocket.connect((rendererIP, 5002))
print("Connected to renderer.")

while True:
    command = input("Enter command: ")
    commandSplit = command.split()
    if command.lower() == "list":
        serverSocket.send(b"List\n0\n")
        manifestMsg = serverSocket.recv(5000).split()
        if manifestMsg[1] != b"-1":
            if manifestMsg[0] == b"List" and manifestMsg[1] == b"1":
                iterMsg = iter(manifestMsg)
                next(iterMsg)
                next(iterMsg)
                for items in iterMsg:
                    print(items.decode('UTF-8'))
            else:
                serverSocket.send(b"List\n-1")
    elif commandSplit[0].lower() == "play":
        rendererSocket.send(b"Control\n0\nPlay\n" + bytearray(commandSplit[1] + "\n", 'utf8'))
        manifestMsg = rendererSocket.recv(5002).split()
        if manifestMsg[1] != b"-1":
            if manifestMsg[0] != b"Control" or manifestMsg[1] != b"1":
                rendererSocket.send(b"Control\n-1\nPlay")
    elif command.lower() == "pause":
        rendererSocket.send(b"Control\n0\nPause\n")
        manifestMsg = rendererSocket.recv(5002).split()
        if manifestMsg[1] != b"-1":
            if manifestMsg[0] != b"Control" or manifestMsg[1] != b"1":
                rendererSocket.send(b"Control\n-1\nPause")
    elif command.lower() == "resume":
        rendererSocket.send(b"Control\n0\nResume\n")
        manifestMsg = rendererSocket.recv(5002).split()
        if manifestMsg[1] != b"-1":
            if manifestMsg[0] != b"Control" or manifestMsg[1] != b"1":
                rendererSocket.send(b"Control\n-1\nResume")
    else:
        print("Invalid Command")
