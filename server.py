import socket
import threading
import os

HEADER = 64
PORT = 5070
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "bye"
UPLOADS_FOLDER = "uploads/"

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
            elif message.startswith("@"):
                private_chat(message, nickname, private_connections, conn, addr)
            elif message.startswith("!UPLOAD"):
                file_name = message[8:]
                file_size_msg = conn.recv(1024).decode(FORMAT)
                print(file_size_msg)
                file_size = int(file_size_msg[10:])

                # receive file content and buffer it
                file_content = b""
                accum_size = 0
                while True:
                    file_data = conn.recv(1024)
                    if not file_data:
                        break
                    accum_size += len(file_data)
                    file_content += file_data
                    if accum_size >= file_size:
                        break

                # write the file to disk, if file does not exist, create it
                file = open(UPLOADS_FOLDER + file_name, "wb")

                file.write(file_content)
                file.close()
                # send an acknowledgement to the client
                # conn.send("".encode(FORMAT))
                broadcast(f"{nickname} sent a file: {file_name}".encode(FORMAT))
            elif message.startswith("!DOWNLOAD"):
                file_name = message[10:]
                try:
                    file = open(UPLOADS_FOLDER + file_name, "rb")
                except:
                    conn.send("File not found".encode(FORMAT))
                    return
                
                # send the file
                conn.send(f"!UPLOAD {file_name}".encode(FORMAT))
                conn.send(f"FILE_SIZE {os.path.getsize(UPLOADS_FOLDER + file_name)}".encode(FORMAT))
                file_data = file.read(1024)
                while file_data:
                    conn.send(file_data)
                    file_data = file.read(1024)
                file.close()
                # conn.shutdown(socket.SHUT_WR)
                print("File sent to client.")

            elif message != "":
                print(f"[{addr}] ({nickname}): {message}")
                broadcast(f"{nickname}: {message}".encode(FORMAT))
        except Exception as e:
            print(e)
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