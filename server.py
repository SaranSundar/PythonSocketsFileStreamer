# This is the server. It serves the controller a list of media files. It also serves the renderer frames
# stackexchange referenced pagm "python.accept non-blocking?"

import os
import select
import socket

# Entry point.
from serveFrame import serveFrame

print("This is the server program.")
# Create manifest list pre-made message
manifest = os.listdir("serverData")
print(manifest)
print("manifest items: ", len(manifest))
manifestMsg = "List\n1\n"  # + str(len(manifest))
for item in manifest:
    manifestMsg += "\n" + item
print("Manifest Message: " + manifestMsg)
# end of creating manifest message
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("", 5000))
s.listen(5)
# current sockets.
mySockets = [s]

while True:
    # we wait for an event to occur among mySockets
    ready, writeable, errored = select.select(mySockets, [], [])
    for current in ready:
        # the event was an incoming connection
        if current is s:
            (newsocket, newaddress) = s.accept()
            mySockets.append(newsocket)
            print("Added a new connection")
        # the event was a message to handle
        else:
            r = current.recv(5000)
            # if empty, then someone died. Remove their socket.
            if len(r) < 1:
                mySockets.remove(current)
                print("Deleted dead person")
                continue
            print(r)
            words = r.split(b'\n')
            # all messages have at least 2 headers.
            if len(words) < 2:
                print("Received uninterpretable message (not enough headers)")
                continue
            # if we get a list request, respond with our premade manifest message
            if words[0] == b"List":
                if words[1] == b"0":
                    current.send(str.encode(manifestMsg))
                    print("Served List Request")
                elif words[1] != b"-1":
                    current.send(b"List\n-1")
                    print("Received unexpected list message: ", r)

            # we don't do anything with control messages.
            # check that its not -1 to prevent infinite loops. "Not valid" "No - You're not valid!"
            elif words[0] == b"Control" and words[1] != b"-1":
                print("Received unexpected control message: ", r)
                current.send(b"Control\n-1")

            elif words[0] == b"Stream":
                # we only handle requests.
                if words[1] == b"0":
                    # stream requests have to have 4 headers
                    if len(words) < 4:
                        print("Received improper stream request (too short)")
                        current.send(b"Stream\n-1")
                        continue
                    # extract filename and frame headers.
                    requestedFile = words[2].decode()
                    requestedFrame = int(words[3])
                    # call serveFrame
                    if requestedFile in manifest:
                        sending = serveFrame(requestedFile, requestedFrame)
                        print("Sending: ", sending)
                        current.send(sending)
                    else:
                        print("Requested file not found: " + requestedFile)
                        current.send(b"Stream\n-1")
                elif words[1] != b"-1":
                    current.send(b"Stream\n-1")
                    print("Received unexpected stream message: ", r)
            else:
                print("Received unexpected unclassified message: ", r)
