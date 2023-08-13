import socket
import threading
from tkinter import *
from tkinter import Tk, Entry, messagebox

HEADER = 1024
PORT = 5070
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!BYE"
SERVER = "192.168.0.102" #IP of server
FONT = "Helvetica"

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
    client.connect(ADDR)

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
            SERVER=serverIP
            connectToServer()
            recieveThread = threading.Thread(target = self.recieve)
            recieveThread.start()

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
            text = "Contact list",
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
            text = "Name of your friend",
            bg = "lightblue",
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
            relheight = 1,
            relwidth = 0.2
        )

        textScrollbar = Scrollbar(self.textBoxFrame)
        textScrollbar.place(
            relx = 0.9738,
            rely = 0,
            relheight = 1,
            #relwidth = 0.01
        )
        textScrollbar.config(command=self.textBox.yview)

    def displayOnlineUser(self, friendName):
        #display tag name
        self.onlineList.append(friendName)
        #print(self.onlineList)
        friendLabel = Label(
            self.contactList,
            bg = "white",
            text = friendName,
            borderwidth = 1,
            relief = SOLID
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
                self.onlineLabel[i].destroy()
                self.onlineLabel.remove(self.onlineLabel[i])
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
        self.currentFriend = nameTag
        self.currentScreen.place_forget()
        self.currentScreen = self.onlineScreen[indexName]
        self.appearPrivateSreen(indexName)
        self.currentScreen.see(END)

    def sendFunc(self, message):
        self.textBox.config(state=DISABLED)
        self.entryChat.delete(0, END)
        sendThread = threading.Thread(target=self.write(message))
        sendThread.start()

    def takeName(self, message, symbol):
        return message[3:message.index(symbol)]

    def recieve(self):
        global connected
        while connected:
            try:
                message = client.recv(HEADER).decode(FORMAT)
            except:
                print("Errors occured !!!")
                disconnect()
            if message == "!NICK":
                client.send(nickname.encode(FORMAT))
            elif message != "":
                code = message[0:3]
                if code == "@#@":
                    friendName = message[3:]
                    self.displayOnlineUser(friendName)
                    #pass
                elif code == "#@#":
                    friendList = message[3:].split()
                    for i in range (len(friendList)):
                        self.displayOnlineUser(friendList[i])
                elif code == "#$#":
                    offName = message[3:]
                    self.destroyOfflineUser(offName)
                elif code == "$#$":
                    friendName = self.takeName(message, ":")
                    friendScreen = self.onlineScreen[self.onlineList.index(friendName)] 
                    friendScreen.config(state = NORMAL)
                    friendScreen.insert(END, message[3:] + "\n\n")
                    friendScreen.config(state = DISABLED)
                    friendScreen.see(END)
                elif code == "$%$":
                    friendName = self.takeName(message, "#")
                    friendScreen = self.onlineScreen[self.onlineList.index(friendName)] 
                    friendScreen.config(state = NORMAL)
                    friendScreen.insert(END, message[4 + len(friendName):] + "\n\n")
                    friendScreen.config(state = DISABLED)
                    friendScreen.see(END)
                else:
                    print(message)
                    self.textBox.config(state = NORMAL)
                    self.textBox.insert(END, message + "\n\n")
                    self.textBox.config(state = DISABLED)
                    self.textBox.see(END)

    def addPrivateCode(self, friendName, message):
        return "@" + friendName + " " + message

    def write(self, message):
        try:

            if (message != ""):
                if self.currentFriend != "GROUP CHAT":
                    client.send(self.addPrivateCode(self.currentFriend, message).encode(FORMAT))
                else:
                    client.send(message.encode(FORMAT))
        except:
            print("Errors 2 occured !!!")
        if message == DISCONNECT_MESSAGE:
            connected = False

start = socketClient()
