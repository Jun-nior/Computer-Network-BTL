import socket
import threading

HEADER = 64
PORT = 5070
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.56.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #sock stream is TCP protocol
client.connect(ADDR)

nickname = input("Enter a nickname: ")

connected = True

def receive():
    global connected
    while connected:
        try:
            message = client.recv(1024).decode(FORMAT)
            if message == "!NICK":
                client.send(nickname.encode(FORMAT))
            elif message != "":
                print(message)
        except:
            print("Errors occured !!!")
            connected = False
            client.close()
                
def send(msg):
    message = msg.encode(FORMAT)
    messageLength = len(message)
    sendLength = str(messageLength).encode(FORMAT)
    sendLength += b' ' * (HEADER - len(sendLength))
    client.send(sendLength)
    client.send(message)

def send_text(message):
    client.send(message.encode(FORMAT))

def send_file(file_path):
    # check if file exists
    try:
        file = open(file_path, "rb")
    except:
        print("File not found")
        return
    
    # send the file
    file_data = file.read(1024)
    while file_data:
        client.send(file_data)
        file_data = file.read(1024)
    file.close()
    client.shutdown(socket.SHUT_WR)
    print("File sent")

def write():
    global connected
    while connected:
        try:
            message = str(input())
            if message.startswith("!FILE"):
                send_text(f"!FILE {message[6:]}")
                send_file(message[6:])
            else:
                send_text(message)

            if message == DISCONNECT_MESSAGE:
                connected = False
        except:
            print("Errors occured !!!")
            connected = False
            client.close()

receiveThread = threading.Thread(target = receive)
receiveThread.start()

writeThread = threading.Thread(target = write)
writeThread.start()
