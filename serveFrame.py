import wave

fileDict = dict()  # filename mapped to (filepointer, location)
CHUNK = 1024
extension = ""  # file extension
f = 0  # file pointer


# This function moves the file pointer to the specified location.
def contentSeek(frame_idx, cur_frame):
    global extension
    global f
    if extension == "wav":
        # try:
        #     f.setpos(frame_idx * CHUNK)
        # except wave.Error:
        #     print("End of wav")
        pass
    else:
        # "if the requested frame is lower than the current frame, reset file to the beginning"
        if frame_idx < cur_frame:
            cur_frame = 0  # reset frame count
            f.seek(0)
        # "While the requested frame is higher than the current frame, increment the current frame"
        while frame_idx > cur_frame:
            cur_frame += 1
            f.readline()


# This function returns the data for the next frame of the specified file.
def getFrame():
    global f
    global extension
    if extension == "txt":
        return f.readline()
    elif extension == "wav":
        # print("Prior: " + str(f.tell()))
        d = f.readframes(CHUNK)
        # print("Post: " + str(f.telll()))
        return d
    else:
        print("unknown file type")
        return None


# Serves frame
# req_file:          Requested file name
# req_frame:         Requested frame number
def serveFrame(req_file, req_frame):
    global fileDict
    global extension
    global f
    extension = req_file.split(".")[-1]
    # if file is not open, open it, and add to dictionary.
    if req_file not in fileDict or extension == "wav" and req_frame == 0:
        if extension == "wav":
            f = wave.open("serverData/" + req_file, "rb")
        else:
            f = open("serverData/" + req_file, "rb")
        fileDict[req_file] = (f, [0])
        print("file opened: ", req_file)
    req = fileDict[req_file]
    f = req[0]
    cur_frame = req[1][0]
    print("File retrieved: ", req)
    # seek to the desired frame
    contentSeek(req_frame, cur_frame)
    # record the new frame in the dictionary
    req[1][0] = req_frame + 1
    # send the frame to the renderer
    frame_result = getFrame()
    if extension == "wav":
        if frame_result == b'':
            frame_result = b"Stream\n1\n\ndone"
    elif extension == 'txt':
        frame_result = b"Stream\n1\n\n" + bytearray(str(frame_result.decode()) + "\n", 'utf8')
    return frame_result
