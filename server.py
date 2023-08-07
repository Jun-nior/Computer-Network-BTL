import socket
import threading

HEADER = 64
PORT = 5070
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "bye"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clientsList = []
nicknames = []
private_connections = []

def broadcast(message):
    for clients in clientsList:
        clients.send(message)

def private_chat(message, nickname, private_connections, conn, addr):
    at_index = message.find("@")  # Find the index of the "@" symbol
    space_index = message.find(" ", at_index)  # Find the index of the first spacing character after the "@"
    
    if space_index == -1:
        print(f"[{addr}] ({nickname}): {message}")
        broadcast(f"{nickname}: {message}".encode(FORMAT))
        return

    recipient = message[at_index+1:space_index]
    real_message = message[space_index:]
    person_exists = False
    
    for connection_info in private_connections:
        wanted_name = connection_info[0]
        if recipient == wanted_name:
            person_exists = True
            recipient_conn = connection_info[1]
            recipient_conn.send(f"Private from {nickname}: {real_message}".encode(FORMAT))
            break
    
    if not person_exists:
        conn.send("The person is not in the chat".encode(FORMAT))

def handleClient(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    index = clientsList.index(conn)
    nickname = nicknames[index]

    connected = True
    while connected:
        try:
            #messageLength = conn.recv(HEADER).decode(FORMAT)
            #if messageLength:
                #messageLength = int(messageLength)
            message = conn.recv(1024).decode(FORMAT)
            if message == DISCONNECT_MESSAGE:
                connected = False
            if message.startswith("@"):
                private_chat(message, nickname, private_connections, conn, addr)
            elif message != "":
                print(f"[{addr}] ({nickname}): {message}")
                broadcast(f"{nickname}: {message}".encode(FORMAT))
        except:
            connected = False
    conn.send(f"You have left the chat".encode(FORMAT))
    conn.close()
    nicknames.remove(nickname)
    clientsList.remove(conn)
    broadcast(f"{nickname} has left the chat!".encode(FORMAT))
        
def start():
    print("[STARTING] Server is starting ...")
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        conn.send("!NICK".encode(FORMAT))
        nickname = conn.recv(1024).decode(FORMAT)
        
        clientsList.append(conn)
        
        conn.send("Connected to server!\n".encode(FORMAT))
        broadcast(f"{nickname} joined the chat!\n".encode(FORMAT))

        if not nicknames:
            conn.send(f"Nobody is in the chat room!\n".encode(FORMAT))
        else: 
            conn.send(f"People currently in the chat room:\n".encode(FORMAT))
            for people in nicknames:
                conn.send(f"{people}; ".encode(FORMAT))
        
        nicknames.append(nickname)
        private_connections.append([nickname,conn])


        thread = threading.Thread(target = handleClient, args = (conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

start()