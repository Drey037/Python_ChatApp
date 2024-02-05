import socket
import json
import sys
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog
from threading import Thread

class client:
    def __init__(self):
        # Main stuff
        self.name = 0
        self.bufferSize = 1024
        self.guiDone = False
        self.running = True

        self.sockClient = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.sockClient.settimeout(3)

        self.channels=[]
        self.connected = False

        #GUI Threads
        guiThread = Thread(target=self.guiLoop)
        guiThread.start()

        self.emojis = {
        ':grin:' : "\U0001f600",
        ':laugh:' : "\U0001F923",
        ':sad:' : "\U0001F97A",
        ':wink:' : "\U0001F609",
        ':sick:' : "\U0001F922", 
        ':sleepy:' : "\U0001F62A",
        ':kiss:' : "\U0001F618",
        ':cry:' : "\U0001F62D",
        ':heart:' : "\U0001F497",
        ':poop:' : "\U0001F4A9",
        ':angry:' : "\U0001F621"
        }
    
    def getEmojis(self, message):
        scan = message.split()

        i = 0
        for word in scan:
            if word in self.emojis:
                scan[i] = self.emojis[word]
            i = i + 1
        
        return ' '.join(scan)


    
    def doCommand(self, sentCommand):
        command = sentCommand.split()
        match command[0]:
            case "0":
                return True

            case "/join":
                if self.connected:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: You are already connected\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Make sure to put valid IP address and port number")
                    return True
                else:
                    self.sockClient = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
                    self.sockClient.settimeout(3)
                    if len(command) < 3 or len(command) > 3:
                        self.chatArea.config(state='normal')
                        self.chatArea.insert('end', "Error: Make sure to put valid IP address and port number\n", 'red')
                        self.chatArea.yview('end')
                        self.chatArea.config(state='disabled')

                        print("Error: Make sure to put valid IP address and port number")
                        return True
                    
                    if not command[2].isdigit():
                        self.chatArea.config(state='normal')
                        self.chatArea.insert('end', "Error: Make sure to put valid port number\n", 'red')
                        self.chatArea.yview('end')
                        self.chatArea.config(state='disabled')

                        print("Error: Make sure to put valid port number")
                        return True

                    ipPort = (command[1], int(command[2]))
                    msg = json.dumps({"command":"join"})

                    print(msg)

                    try:
                        self.sockClient.connect(ipPort)
                        self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                        received = self.sockClient.recvfrom(self.bufferSize)
                        message = json.loads(received[0])

                        self.chatArea.config(state='normal')
                        self.chatArea.insert('end', message["message"] + "\n", 'green')
                        self.chatArea.yview('end')
                        self.chatArea.config(state='disabled')

                        print(message["message"])

                        #starts the reading input
                        self.receiveStart = Thread(target = self.receive)
                        self.receiveFlag = True
                        self.receiveStart.start()
                        self.connected = True
                    except socket.error:
                        self.chatArea.config(state='normal')
                        self.chatArea.insert('end', "Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.\n", 'red')
                        self.chatArea.yview('end')
                        self.chatArea.config(state='disabled')

                        print("Error: Connection to the Message Board Server has failed! Please check IP Address and Port Number.")    
                return True


            case "/leave":
                if len(command) > 1:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Wrong command use. Use '/leave' only\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Wrong command use. Use '/leave' only")
                    return True

                msg = json.dumps({"command":"leave"})

                try:
                    self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                    received = self.sockClient.recvfrom(self.bufferSize)
                    message = json.loads(received[0])

                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', message["message"] + "\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print(message["message"])

                    #Stops the reading input
                    self.receiveFlag = False
                    self.receiveStart.join()
                    self.sockClient.close()
                    self.connected = False
                    self.name = 0
                    self.chatLabel.config(text="Handle: ", bg="lightgray", foreground='black')
                except socket.error:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Disconnection failed. Please connect to the server first.\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Disconnection failed. Please connect to the server first.")
                return True

            case "/register":
                if len(command) > 2 or len(command) < 2:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Invalid handle. Should only be 1 word\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Invalid handle. Should only be 1 word")
                    return True

                if command[1] == '0':
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Invalid handle. Don't use 0\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')
                    print("Error: Invalid handle. Don't use 0")
                    return True


                msg = json.dumps({"command":"register", "handle": command[1]})

                try:
                    self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                except socket.error:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Registration failed. Please connect to the server first.\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Registration failed. Please connect to the server first.")
                return True

            case "/all":
                if len(command) < 2:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Message to all not sent. Please input a message when sending\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Message to all not sent. Please input a message when sending")
                    return True

                command.remove("/all")
                message = ' '.join(command)
                msg = json.dumps({"command":"all", "message": message})

                try:
                    self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                except socket.error:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Message to all is not sent. Make sure that you are connected to the server\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Message to all is not sent. Make sure that you are connected to the server")
                return True

            case "/msg":
                if len(command) < 3:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Message to all not sent. Please input handle and message when sending\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Message to all not sent. Please input handle and message when sending")
                    return True

                command.pop(0)
                user = command.pop(0)
                message = ' '.join(command)
                msg = json.dumps({"command":"msg", "handle": user, "message": message})

                try:
                    self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                except socket.error:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Direct message is not sent. Please make sure you are connected\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Direct message is not sent. Please make sure you are connected")
                return True

            case "/close":
                msg = json.dumps({"command":"close"})
                try:
                    self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                    received = self.sockClient.recvfrom(self.bufferSize)
                    message = json.loads(received[0])
                    print(message["message"])

                    #Stops the reading input
                    self.receiveFlag = False
                    self.connected = False
                    self.receiveStart.join()
                    self.sockClient.close()
                except socket.error:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Server closure failed. Please connect to the server first.\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')
                    
                    print("Error: Server closure failed. Please connect to the server first.")
                return False

            case "/users":
                msg = json.dumps({"command":"users"})
                try:
                    self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                except socket.error:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Command error. Connect to server first\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Command error. Connect to server first")
                return True

            case "/?":
                # GUI Show
                self.chatArea.config(state='normal')
                self.chatArea.insert('end', 'List of commands:\n', 'gray')
                self.chatArea.insert('end', '/join <IP Address> <Port> -> Join a server\n', 'gray')
                self.chatArea.insert('end', "/leave -> Leave a server\n", 'gray')
                self.chatArea.insert('end', "/register <Handle or nickname> -> Register yourself a handle in a server\n", 'gray')
                self.chatArea.insert('end', "/all <Message> -> Send a message to all users registered in the server\n", 'gray')
                self.chatArea.insert('end', "/msg <Handle or nickname> <Message> -> Send a direct message to someone registered in the server\n", 'gray')
                self.chatArea.insert('end', "/close -> Close the server\n", 'gray')
                self.chatArea.insert('end', "/users -> Show a list of registered users in the server\n", 'gray')
                self.chatArea.insert('end', "/emojis -> Show a list of emojis\n", 'gray')

                #Commands about channel
                self.chatArea.insert('end', "/new_ch <channel name> -> Create new channel in server\n", 'gray')
                self.chatArea.insert('end', "/join_ch <channel name> -> Join a channel\n", 'gray')
                self.chatArea.insert('end', "/leave_ch <channel name> -> leave a channel\n", 'gray')
                self.chatArea.insert('end', "/msg_ch <channel name> <message> -> Send a message to a channel\n", 'gray')
                self.chatArea.insert('end', "/user_ch -> Show a list of joined channels of the user\n", 'gray')
                self.chatArea.insert('end', "/server_ch -> Show a list of channels in the server\n", 'gray')

                self.chatArea.yview('end')
                self.chatArea.config(state='disabled')

                return True

            case '/emojis':
                self.chatArea.config(state='normal')

                self.chatArea.insert('end', 'List of Emojis: ' + '\n', 'black')

                for emoji in self.emojis:
                    self.chatArea.insert('end', emoji + " -  " + self.emojis[emoji] + '\n', 'black')
                self.chatArea.yview('end')
                self.chatArea.config(state='disabled')

                return True

            #Shows all channels of the server
            case '/server_ch':
                msg = json.dumps({"command":"server_ch"})
                try:
                    self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                except socket.error:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Command error. Connect to server first\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Command error. Connect to server first")
                return True

            #Shows all joined channels of the user
            case '/user_ch':
                if len(self.channels) > 0:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', 'List of joined channels: ' + '\n', 'black')

                    for channel in self.channels:
                        self.chatArea.insert('end', channel + '\n', 'black')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')
                else:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', 'You are not part of any channel' + '\n', 'black')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                return True

            #Create new channel
            case '/new_ch':
                if len(command) > 2 or len(command) < 2:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Invalid channel name. Should only be 1 word\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Invalid channel name. Should only be 1 word")
                    return True

                if command[1] == '0':
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Invalid channel name. Don't use 0\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')
                    print("Error: Invalid channel name. Don't use 0")
                    return True


                msg = json.dumps({"command":"new_ch", "channel": command[1]})

                try:
                    self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                except socket.error:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Channel creation failed. Please connect to the server first.\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Channel creation failed. Please connect to the server first.")
                return True

            #Join a channel
            case '/join_ch':
                if len(command) > 2 or len(command) < 2:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Invalid channel name. Should only be 1 word\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Invalid channel name. Should only be 1 word")
                    return True

                msg = json.dumps({"command":"join_ch", "channel": command[1]})

                try:
                    self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                except socket.error:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Attempt to join channel failed. Please connect to the server first.\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Attempt to join channel failed. Please connect to the server first.")
                return True

            #Leave a channel
            case '/leave_ch':
                if len(command) > 2 or len(command) < 2:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Invalid channel name. Should only be 1 word\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Invalid channel name. Should only be 1 word")
                    return True

                msg = json.dumps({"command":"leave_ch", "channel": command[1]})

                try:
                    self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                except socket.error:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Attempt to leave channel failed. Please connect to the server first.\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Attempt to leave channel failed. Please connect to the server first.")
                return True

            #Message in a channel
            case '/msg_ch':
                if len(command) < 3:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Message to channel not sent. Please input the channel then message when sending\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Message to all not sent. Please input the channel then message when sending")
                    return True

                command.remove("/msg_ch")
                channelSend = command[0]
                command.remove(command[0])
                message = ' '.join(command)
                msg = json.dumps({"command":"msg_ch", "message": message, 'channel': channelSend})

                try:
                    self.sockClient.sendall(bytes(msg, encoding="utf-8"))
                except socket.error:
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', "Error: Message to channel is not sent. Make sure that you are connected to the server\n", 'red')
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    print("Error: Message to channel is not sent. Make sure that you are connected to the server")
                return True

            
            case other:
                # GUI Show Error
                self.chatArea.config(state='normal')
                self.chatArea.insert('end', "Error: Command doesn't exist\n", 'red')
                self.chatArea.yview('end')
                self.chatArea.config(state='disabled')

                print("Error: Command doesn't exist\n")
                return True

    def receive(self):
        while True:
            if not self.receiveFlag:
                break
            try:
                received = self.sockClient.recvfrom(self.bufferSize)
                message = json.loads(received[0])

                #If GUI is done updating
                if self.guiDone:
                    checkedMsg = self.getEmojis(message["message"])
                    # Add message to the GUI
                    self.chatArea.config(state='normal')
                    self.chatArea.insert('end', checkedMsg + '\n', self.colorText(message["message"]))
                    self.chatArea.yview('end')
                    self.chatArea.config(state='disabled')

                    #Print in terminal
                    print(checkedMsg)
            except socket.error:
                continue

    def input(self, event):
        command = self.msgInput.get('1.0', 'end')
        #command = input("Enter command: ")
        print(command)
        self.stopper = self.doCommand(command)
        self.msgInput.delete('1.0', 'end')

    def inputButton(self):
        command = self.msgInput.get('1.0', 'end')
        #command = input("Enter command: ")
        print(command)
        self.stopper = self.doCommand(command)
        self.msgInput.delete('1.0', 'end')

    def colorText(self, message):
        first = message.split()
        match first[0]:
            case 'Error:':
                return 'red'

            case '[From':
                return 'blue'

            case '[To':
                return 'gray'

            case 'Welcome':
                self.name = first[1][:-1]
                self.chatLabel.config(text="Handle: " + self.name, bg="lightgray", foreground='blue')
                return 'green'

            case 'Connection':
                return 'green'

            case 'Channel:Created':
                self.channels.append(first[6][:-1])
                return 'purple'

            case 'Channel:Welcome':
                self.channels.append(first[3][:-1])
                return 'purple'

            case 'Channel:Goodbye!':
                self.channels.remove(first[3])
                return 'purple'

            case 'Channel':
                return 'purple'
            
            case 'List':
                return 'gray'

            case other:
                return 'black'

    #GUI Stuff
    def guiLoop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")
        self.win.title("Chat Window")

        self.chatLabel = tkinter.Label(self.win, text="Handle: ", bg="lightgray")
        self.chatLabel.config(font=("Arial", 12))
        self.chatLabel.pack(padx=20, pady=5)

        self.chatArea = tkinter.scrolledtext.ScrolledText(self.win)
        self.chatArea.pack(padx=20, pady=5)
        self.chatArea.config(font=("Arial", 12), state="disabled")
        
        #Chat Area color text configs
        self.chatArea.tag_config("red", foreground="red")
        self.chatArea.tag_config("gray", foreground="gray")
        self.chatArea.tag_config("blue", foreground="blue")
        self.chatArea.tag_config("black", foreground="black")
        self.chatArea.tag_config("green", foreground="green")
        self.chatArea.tag_config("lightgray", foreground="lightgray")
        self.chatArea.tag_config("purple", foreground="purple")

        self.msgLabel = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msgLabel.config(font=("Arial", 12))
        self.msgLabel.pack(padx=20, pady=5)

        self.msgInput = tkinter.Text(self.win, height=3)
        self.msgInput.pack(padx=20, pady=5)

        self.win.bind("<Return>", self.input)
        self.button = tkinter.Button(self.win, text="send", command=self.inputButton)
        self.button.config(font=("Arial", 12))
        self.button.pack(padx=20, pady=5)

        self.guiDone = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()


    def stop(self):
        self.running = False
        self.win.destroy()
        self.sockClient.close()
        exit(0)

#START
start = client()

            


        






