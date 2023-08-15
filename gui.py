import socket
import threading
from tkinter import *
from tkinter import Tk, Entry, messagebox, filedialog
import os

HEADER = 1024
PORT = 5070
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "bye"
SERVER = "172.28.144.1" #IP of server
FONT = "Helvetica"
DOWNLOADS_FOLDER = "downloads/"

nickname = ""
connected = True
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #sock stream is TCP protocol

def disconnect():
    global client
    global connected
    connected = False
    client.close()

def connectToServer():
    ADDR = (SERVER, PORT)
    try:   
        client.connect(ADDR)
    except:
        print("cannot connect !!!")

class socketClient:
    
    relYlist = 0 #for online list label
    tagFriendHeight = 0.1
    onlineLabel = []
    onlineScreen = []
    onlineList = []
    #self.currentScreen = self.textBox

    def __init__(self):
        self.chatWindow = Tk()
        self.chatWindow.withdraw()

        #log in
        self.login = Toplevel()
        self.login.resizable(
            width=False, 
            height=False
        )
        self.login.title("Login")
        self.login.configure(width=400, height=400)

        self.enterMsg = Label(
            self.login, 
            text="ENTER THE CHAT ROOM",
            justify=CENTER, 
            font=FONT + " 14 bold"
        )
        self.enterMsg.place(
            relheight=0.15, 
            relx=0.2, 
            rely=0.04
        )

        #input name
        self.labelName = Label(
            self.login, 
            text="Name", 
            font=FONT + " 12 bold"
        )
        self.labelName.place(
            relheight=0.2, 
            relx=0.1, 
            rely=0.15
        )

        self.inputName = Entry(
            self.login, 
            font=FONT + " 14", 
            border=2, 
            justify=CENTER
        )
        self.inputName.place(
            relwidth=0.8, 
            relheight=0.10, 
            relx=0.1,
            rely=0.3
        )

        #input IP of server
        self.labelServer = Label(
            self.login, 
            text="IP of server", 
            font=FONT + " 12 bold"
        )
        self.labelServer.place(
            relheight=0.2, 
            relx=0.1, 
            rely=0.4
        )

        self.inputServer = Entry(
            self.login, 
            font=FONT + " 14", 
            border=2, 
            justify=CENTER
        )
        self.inputServer.place(
            relwidth=0.8, 
            relheight=0.10, 
            relx=0.1,
            rely=0.55
        )
        
        #login button
        self.loginBtn = Button(
            self.login, 
            text="LOG IN",
            font=FONT + " 12 bold",
            command=lambda: self.goToChat(self.inputName.get(), self.inputServer.get())
        )
        self.loginBtn.place(relx=0.4, rely=0.7)
        
        
        self.chatWindow.mainloop()

    def goToChat(self, name, serverIP):
        if (name == '' or serverIP == ''):
            messagebox.showerror("Error !!!", "Please enter a name and server IP.")
        else:
            self.login.destroy()
            
            #set name and server
            global nickname
            global SERVER
            nickname = name
            #SERVER = serverIP

            self.chatBox(name)
            self.displayOnlineUser("GROUP CHAT")
            #self.onlineScreen[0].place()
            self.currentFriend = "GROUP CHAT"
            #start a thread
            connectToServer()
            recieveThread = threading.Thread(target = self.recieve)
            recieveThread.start()

    def send(msg):
        message = msg.encode(FORMAT)
        messageLength = len(message)
        sendLength = str(messageLength).encode(FORMAT)
        sendLength += b' ' * (HEADER - len(sendLength))
        client.send(sendLength)
        client.send(message)

    def send_text(self, message):
        client.send(message.encode(FORMAT))

    def send_file(self, file_path):
        # check if file exists
        try:
            print(file_path)
            file = open(file_path, "rb")
        except:
            print("File not found")

        # send the file
        file_size = os.path.getsize(file_path)
        #self.send_text(f"FILE_SIZE {file_size}")
        self.send_text(f"FILE_SIZE {file_size}" + ' '*(1024 -len(f"FILE_SIZE {file_size}")))
        file_data = file.read(1024)
        while file_data:
            client.send(file_data)
            file_data = file.read(1024)
        file.close()
        # client.shutdown(socket.SHUT_WR)
        print("File sent to server.")

    def sendFileBtnFunc(self): #need to create thread
        filePath = filedialog.askopenfilename(title="Upload")
        if (filePath != ""):
            print(filePath)
            fileName = os.path.basename(filePath)
            self.send_text(f"!UPLOAD {fileName}") #just send file name
            self.send_file(filePath)

    def chatBox(self, name):
        self.chatWindow.deiconify()
        # self.chatWindow.title("Chat Box")
        # self.chatWindow.resizable(width=FALSE, height=FALSE)
        # self.chatWindow.configure(width=700, height=800)

        self.chatWindow.title("Chat Box")
        self.chatWindow.resizable(width=FALSE, height=FALSE)
        self.chatWindow.configure(width=700, height=700)

        self.contactListLabel = Label(
            self.chatWindow,
            text = "Online users",
            font = FONT + " 12 bold"
        )
        self.contactListLabel.place(
            relheight = 0.1,
            relwidth = 0.25,
            relx = 0,
            rely = 0
        )

        self.contactList = Frame(
            self.chatWindow,
            bg = "grey"
        )
        self.contactList.place(
            relx = 0,
            rely = 0.1,
            relheight = 0.9,
            relwidth = 0.25
        )

        self.friendName = Label(
            self.chatWindow,
            text = name,
            bg = "lightblue",
            font=FONT + " 17 bold"
        )
        self.friendName.place(
            relx = 0.25,
            rely = 0,
            relheight = 0.1,
            relwidth = 0.75
        )

        self.textBoxFrame = Frame(
            self.chatWindow,
            bg = "red",
        )
        self.textBoxFrame.place(
            relx = 0.25,
            rely = 0.1,
            relheight = 0.8,
            relwidth = 0.75
        )

        self.textBox = Text(
            self.textBoxFrame,
            bg = "white",
        )
        self.textBox.place(
            relx = 0,
            rely = 0,
            relheight = 1,
            relwidth = 1
        )
        self.textBox.config(state=DISABLED)
        self.currentScreen = self.textBox
        self.onlineScreen.append(self.textBox)

        self.inputChat = Frame(
            self.chatWindow,
            bg = "grey"
        )
        self.inputChat.place(
            relx = 0.25,
            rely = 0.9,
            relheight = 0.1,
            relwidth = 0.75
        )

        self.entryChat = Entry(
            self.inputChat,
            font = FONT + " 14"
        )
        self.entryChat.place(
            relx = 0,
            rely = 0,
            relheight = 1,
            relwidth = 0.8
        )

        self.sendBtn = Button(
            self.inputChat,
            text = "send",
            font = FONT + " 10",
            command=lambda: self.sendFunc(self.entryChat.get())
        )
        self.sendBtn.place(
            relx = 0.8,
            rely = 0,
            relheight = 0.5,
            relwidth = 0.2
        )

        self.entryChat.bind("<Return>", lambda event, arg = self.entryChat.get(): self.enterEvent(event, arg))
        # lambda event, arg = friendName: self.clickLabel(event, arg)

        self.sendFileBtn = Button(
            self.inputChat,
            text = "send file",
            font = FONT + " 10",
            command=lambda: self.sendFileBtnFunc()
        )
        self.sendFileBtn.place(
            relx = 0.8,
            rely = 0.5,
            relheight = 0.5,
            relwidth = 0.2
        )
        textScrollbar = Scrollbar(self.textBoxFrame)
        textScrollbar.place(
            relx = 0.9738,
            rely = 0,
            relheight = 1,
            #relwidth = 0.01
        )
        textScrollbar.config(command=self.currentScreen.yview)

    def displayOnlineUser(self, friendName):
        #display tag name
        self.onlineList.append(friendName)
        #print(self.onlineList)
        friendLabel = Label(
            self.contactList,
            bg = "white",
            text = friendName,
            borderwidth = 1,
            relief = SOLID,
            font="Arial 10"
        )
        friendLabel.place(
            relx = 0,
            rely = self.relYlist,
            relheight = self.tagFriendHeight,
            relwidth = 1
        )
        friendLabel.bind('<Button-1>', lambda event, arg = friendName: self.clickLabel(event, arg))

        self.onlineLabel.append(friendLabel)
        self.relYlist += self.tagFriendHeight

        #create private screen
        if (friendName != "GROUP CHAT"):
            privateScreen = Text(
                self.textBoxFrame,
                bg = "white",
            )
            privateScreen.place(
                relx = 0,
                rely = 0,
                relheight = 1,
                relwidth = 1
            )
            privateScreen.config(state=DISABLED)
            privateScreen.place_forget()
            self.onlineScreen.append(privateScreen)

    def destroyOfflineUser(self, friendName):
        for i in range (len(self.onlineList)):
            if self.onlineLabel[i].cget("text") == friendName:
                print("1111")
                self.onlineLabel[i].destroy()
                self.onlineScreen[i].destroy()
                self.onlineLabel.remove(self.onlineLabel[i])
                self.onlineScreen.remove(self.onlineScreen[i])
                self.onlineList.pop(i)
                self.tagNameBubble(i)
                break

    def tagNameBubble(self, index):
        currentRely = self.tagFriendHeight * (index + 1)
        for i in range (index, len(self.onlineList)):
            self.onlineLabel[i].place(rely = currentRely - self.tagFriendHeight)
            currentRely += self.tagFriendHeight
        self.relYlist -= self.tagFriendHeight 

    def clickLabel(self, event, nameTag):
        self.clickTagName(nameTag)

    def appearPrivateSreen(self, index):
        self.onlineScreen[index].place(
            relx = 0,
            rely = 0,
            relheight = 1,
            relwidth = 1
        )

    def clickTagName(self, nameTag):
        indexName = self.onlineList.index(nameTag)
        indexCurrent = self.onlineScreen.index(self.currentScreen)
        self.onlineLabel[indexCurrent].config(bg="white")

        self.currentFriend = nameTag
        self.currentScreen.place_forget()
        self.currentScreen = self.onlineScreen[indexName]
        self.appearPrivateSreen(indexName)
        self.currentScreen.see(END)
        self.onlineLabel[indexName].config(bg="#ffe4e1")

        textScrollbar = Scrollbar(self.textBoxFrame)
        textScrollbar.place(
            relx = 0.9738,
            rely = 0,
            relheight = 1,
            #relwidth = 0.01
        )
        textScrollbar.config(command=self.currentScreen.yview)

    def enterEvent(self, event, message):
        self.sendFunc(message)

    def sendFunc(self, message):
        self.textBox.config(state=DISABLED)
        self.entryChat.delete(0, END)
        sendThread = threading.Thread(target=self.write(message))
        sendThread.start()

    def takeName(self, message, symbol):
        return message[3:message.index(symbol)]

    def writeText(self, text, index):
        screen = self.onlineScreen[index]
        screen.config(state = NORMAL)
        screen.insert(END, text)
        screen.config(state = DISABLED)
        screen.see(END)

    def recieveFile(self, message):
        file_path = message[10:]
        print(file_path)
        file_size_msg = client.recv(1024).decode(FORMAT)
        file_size = int(file_size_msg[10:])
        DOWNLOADS_FOLDER = filedialog.askdirectory(title = "Dowload")
        if (DOWNLOADS_FOLDER != ""):
            file = open(DOWNLOADS_FOLDER + '/'+ file_path, "wb")
            file_data = client.recv(1024)
            while file_data:
                file.write(file_data)
                accum_len = len(file_data)
                if accum_len >= file_size:
                    break
                file_data = client.recv(1024)
            file.close()
            print("File downloaded from server.") 

    def processMessage(self, message):
        if message == "!NICK":
            client.send(nickname.encode(FORMAT))
        elif message != "":
            code = message[0:3]
            if code == "@#@":
                friendName = message[3:]
                self.displayOnlineUser(friendName)
            elif code == "#@#": #new connection, for appear current online 
                friendList = message[3:].split()
                for i in range (len(friendList)):
                    self.displayOnlineUser(friendList[i])
            elif code == "#$#": #for destroy offline user
                print("hhh")
                print(message)
                offName = self.takeName(message, " ")
                print("kkk")
                print(offName)
                self.destroyOfflineUser(offName)
                self.writeText(message[3:] + "\n\n", 0)
            elif code == "$#$": #for recipient in private chat
                print("bbb")
                friendName = self.takeName(message, ":")
                self.writeText(message[3:] + "\n\n", self.onlineList.index(friendName)) 
            elif code == "$%$": #for sender in private chat
                print("ccc")
                friendName = self.takeName(message, "#")
                print(friendName) 
                self.writeText(message[4 + len(friendName):] + "\n\n", self.onlineList.index(friendName))
            elif message.startswith("!DOWNLOAD"):
                self.recieveFile(message)
            else: #group chat
                print(message)
                print("xxx")
                self.writeText(message + "\n\n", 0) 

    def recieve(self):
        global connected
        while connected:
            try:
                message = client.recv(HEADER).decode(FORMAT)
                if message == DISCONNECT_MESSAGE:
                    connected = False
            except:
                print("Errors occured !!!")
                disconnect()
            self.processMessage(message)
            # if message == "!NICK":
            #     client.send(nickname.encode(FORMAT))
            # elif message != "":
            #     code = message[0:3]
            #     if code == "@#@":
            #         friendName = message[3:]
            #         self.displayOnlineUser(friendName)
            #     elif code == "#@#": #new connection, for appear current online 
            #         friendList = message[3:].split()
            #         for i in range (len(friendList)):
            #             self.displayOnlineUser(friendList[i])
            #     elif code == "#$#": #for destroy offline user
            #         print("hhh")
            #         print(message)
            #         offName = self.takeName(message, " ")
            #         print("kkk")
            #         print(offName)
            #         self.destroyOfflineUser(offName)
            #         self.writeText(message[3:] + "\n\n", 0)
            #     elif code == "$#$": #for recipient in private chat
            #         print("bbb")
            #         friendName = self.takeName(message, ":")
            #         self.writeText(message[3:] + "\n\n", self.onlineList.index(friendName)) 
            #     elif code == "$%$": #for sender in private chat
            #         print("ccc")
            #         friendName = self.takeName(message, "#")
            #         print(friendName) 
            #         self.writeText(message[4 + len(friendName):] + "\n\n", self.onlineList.index(friendName))
            #     elif message.startswith("!DOWNLOAD"):
            #         self.recieveFile(message)
            #     else: #group chat
            #         print(message)
            #         print("xxx")
            #         self.writeText(message + "\n\n", 0) 
        print("B")

    def addPrivateCode(self, code, message):
        return code + message

    def write(self, message):
        try:
            if (message != ""):
                if self.currentFriend != "GROUP CHAT":
                    client.send(self.addPrivateCode("@"+self.currentFriend + " ", message).encode(FORMAT))
                else:
                    client.send(message.encode(FORMAT))
                    if message == DISCONNECT_MESSAGE:
                        connected = False
        except:
            print("Errors 2 occured !!!")
        print("a")
        

start = socketClient()
