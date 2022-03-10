# DataClient1.py

from threading import Thread
import socket, time

VERBOSE = False
IP_ADDRESS = "192.168.86.53"
IP_PORT = 8000
sock = None

def debug(text):
    if VERBOSE:
        print("Debug:---", text)

# ------------------------- class Receiver ---------------------------
class Receiver(Thread):
    def run(self):
        debug("Receiver thread started")
        while True:
            try:
                rxData = self.readServerData()
            except:
                debug("Exception in Receiver.run()")
                isReceiverRunning = False
                closeConnection()
                break
        debug("Receiver thread terminated")

    def readServerData(self):
        print("Calling readResponse")
        bufSize = 4096
        data = ""
        while data[-1:] != "\0": # reply with end-of-message indicator
            try:
                blk = sock.recv(bufSize).decode()
                if blk != None:
                    print("Received data block",blk, "from server, len:",len(blk))
                else:
                    print("sock.recv() returned with None")
            except:
                raise Exception("Exception from blocking sock.recv()")
            data += blk
        print("Data received:", data)
# ------------------------ End of Receiver ---------------------

def startReceiver():
    debug("Starting Receiver thread")
    receiver = Receiver()
    receiver.start()

def sendCommand(cmd):
    debug("sendCommand() with cmd = " + cmd)
    try:
        # append \0 as end-of-message indicator
        sock.sendall(str.encode(f"{cmd}\0"))
    except:
        print("Exception in sendCommand()")
        closeConnection()

def closeConnection():
    global isConnected
    debug("Closing socket")
    sock.close()
    isConnected = False

def connect():
    global sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    debug("Connecting...")
    try:
        sock.connect((IP_ADDRESS, IP_PORT))
    except:
        debug("Connection failed.")
        return False
    startReceiver()
    return True

isConnected = False

if connect():
    isConnected = True
    print("Connection established")
    time.sleep(1)
    while(isConnected):
        print("Sending command: HELLO...")
        sendCommand("HELLO")
        time.sleep(5)
    if(not isConnected):
        print("DISCONNECTED TO SERVER")
else:
    print(f"Connection to {IP_ADDRESS}:{IP_PORT} failed")
print("done")