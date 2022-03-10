# DataServer1.py

from threading import Thread
import socket
import time
import os

VERBOSE = False
IP_PORT = 8000
P_BUTTON = 24 # adapt to your wiring

def setup():
    # GPIO.setmode(GPIO.BOARD)
    # GPIO.setup(P_BUTTON, GPIO.IN, GPIO.PUD_UP)
    pass

def debug(text):
    if VERBOSE:
        print("Debug:---", text)

# ---------------------- class SocketHandler ------------------------
class SocketHandler(Thread):
    def __init__(self, conn):
        Thread.__init__(self)
        self.conn = conn

    def run(self):
        global isConnected
        debug("SocketHandler started")
        initial_count = 0
        dir = "images/"
        for path in os.listdir(dir):
            if os.path.isfile(os.path.join(dir, path)):
              initial_count += 1
        while True:

            # TODO: replace with picture taking code
            curr_count = 0
            file_list = []
            for path in os.listdir(dir):
              if os.path.isfile(os.path.join(dir, path)):
                curr_count += 1
                file_list.append(os.path.join(dir, path))
            if(curr_count > initial_count):
                print("CURRENTLY",curr_count,"FILES IN IMAGES")
                initial_count = curr_count
                latest_file = max(file_list, key=os.path.getctime)
                self.executeCommand(latest_file)
            time.sleep(5.0)
            
            # block for exiting
            cmd = ""
            try:
                debug("Calling blocking conn.recv()")
                cmd = self.conn.recv(1024).decode()
                print("received command", cmd, "LENGTH:", len(cmd))
            except:
                debug("exception in conn.recv()") 
                # happens when connection is reset from the peer
                break
            #print("Received cmd: " + cmd + " len: " + str(len(cmd)))
            if(cmd[:-1] == "quit"):
                break
        conn.close()
        print("Client disconnected. Waiting for next client...")
        isConnected = False
        debug("SocketHandler terminated")

    def executeCommand(self, cmd):
        debug("Calling executeCommand() with  cmd: " + cmd)
        print("Sending filename")
        self.conn.sendall(str.encode(f"{cmd}\0"))
        # if(cmd[:-1] == "HELLO"):
        #   print("SENDING RESPONSE")
        #   self.conn.sendall(str.encode("HEY THERE\0"))
        # if cmd[:-1] == "go":  # remove trailing "\0"
        #     if GPIO.input(P_BUTTON) == GPIO.LOW:
        #         state = "Button pressed"
        #     else:
        #         state = "Button released"
        #     print("Reporting current state:", state)
        #     self.conn.sendall(state + "\0")
# ----------------- End of SocketHandler -----------------------

setup()
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# close port when process exits:
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
debug("Socket created")
HOSTNAME = "" # Symbolic name meaning all available interfaces
try:
    serverSocket.bind((HOSTNAME, IP_PORT))
except socket.error as msg:
    print("Bind failed", msg[0], msg[1])
    sys.exit()
serverSocket.listen(10)

print("Waiting for a connecting client...")
isConnected = False
while True:
    debug("Calling blocking accept()...")
    conn, addr = serverSocket.accept()
    print("Connected with client at " + addr[0])
    isConnected = True
    socketHandler = SocketHandler(conn)
    # necessary to terminate it at program termination:
    socketHandler.setDaemon(True)  
    socketHandler.start()
    t = 0
    while isConnected:
        print("Server connected at", t, "s")
        time.sleep(10)
        t += 10
