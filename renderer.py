import sys
import time

import pyaudio
import socket
import threading

serverIp = '127.0.0.1'
# Create a socket that actively connects to the server
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print("Connecting to server...")
serverSocket.connect((serverIp, 5000))
print("Connected to server. Now awaiting client controller...")

# Create a socket that passively listens for incoming connections on port 5002
controllerListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
controllerListener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
controllerListener.bind(("", 5002))
controllerListener.listen(1)
# Accepts an incoming connection
controllerSocket, controllerAddress = controllerListener.accept()
print("Client controller connected.")
CHUNK = 1024
line_number = 0
streaming_file = False
file_name = b""

stream = ""
p = pyaudio.PyAudio()


# p.terminate()


def create_audio():
    global stream
    global p
    stream = p.open(format=p.get_format_from_width(2),
                    channels=2,
                    rate=44100,
                    output=True)


def end_audio():
    global stream
    stream.stop_stream()
    stream.close()


def get_from_controller():
    global line_number
    global streaming_file
    global file_name
    global controllerSocket
    while True:
        controller_input = controllerSocket.recv(5000).split(b'\n')

        # Send back an error message to the controller for any List messages
        if controller_input[0] == b"List":
            controllerSocket.send(b"List\n-1\n")
            continue

        # Send back an error message to the controller for any Stream messages
        if controller_input[0] == b"Stream":
            controllerSocket.send(b"Stream\n-1\n")
            continue

        # Renderer only takes action on Control messages
        if controller_input[0] == b"Control":
            # Send an error message if receiving a Control confirmation
            if controller_input[1] != b"0":
                controllerSocket.send(b"Control\n-1\n")
                continue

            # Pause the renderer
            if controller_input[2] == b"Pause":
                streaming_file = False
                controllerSocket.send(b"Control\n1\n")

            # Resume the renderer with the current file
            elif controller_input[2] == b"Resume":
                streaming_file = True
                controllerSocket.send(b"Control\n1\n")

            # The renderer should now be playing something
            elif controller_input[2] == b"Play":
                """ Regardless of renderer's current state, stream file from start """
                # Send controller confirmation
                controllerSocket.send(b"Control\n1\n")
                # Initialize renderer state information
                file_name = controller_input[3]
                line_number = 0
                # If audio file, create audio channel
                if file_name.decode().split(".")[1] == "wav":
                    create_audio()
                # Begin streaming from server
                streaming_file = True


def send_to_server():
    global line_number
    global streaming_file
    global file_name
    global serverSocket
    global stream
    while True:
        if streaming_file and file_name.decode().split(".")[1] == "txt":
            serverSocket.send(b"Stream\n0\n" + file_name + b"\n" + bytearray(str(line_number) + "\n", 'utf8'))
            file_contents = serverSocket.recv(5000).decode()
            # print(file_contents)
            file_contents = file_contents.split("\n")
            line_number += 1
            if len(file_contents) >= 4 and len(file_contents[3]) >= 1:
                output = ""
                for i in range(3, len(file_contents)):
                    output += file_contents[i]
                print(output)
                # Give time to read each line, minimum of quarter second per line
                time.sleep(max(len(output) / 25, 0.25))
            else:
                streaming_file = False
                print("---------------------    END OF FILE    -----------------------")
        elif streaming_file and file_name.decode().split(".")[1] == "wav":
            serverSocket.send(b"Stream\n0\n" + file_name + b"\n" + bytearray(str(line_number) + "\n", 'utf8'))
            file_contents = serverSocket.recv(CHUNK)
            line_number += 1
            # print("File before, ", file_contents)
            # file_contents = file_contents[len(b"Stream\n1\n\n"):]
            # print("File after, ", file_contents)
            # print(file_contents)
            header = b"Stream\n1\n\ndone"  # b"Stream\n1\n\n"
            if file_contents != header:
                while len(file_contents) >= len(header) and file_contents[0:len(header)] == header:
                    file_contents = file_contents[len(header):]
                test = str(file_contents)
                print("File is ", test)
                if "done" not in test:
                    stream.write(file_contents)
            else:
                end_audio()
                streaming_file = False
                file_contents = serverSocket.recv(CHUNK)
                print("File END, ", file_contents)
                print("---------------------    END OF AUDIO    -----------------------")
            time.sleep(0.001)


threading.Thread(target=get_from_controller).start()
threading.Thread(target=send_to_server).start()
