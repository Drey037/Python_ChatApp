import socket
import json


localIP     = "127.0.0.1"
localPort   = 12345
bufferSize  = 1024
users = []
channels = []
stopper = True

# Create a datagram socket
sockServer = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
sockServer.bind((localIP, localPort))

print("UDP server up and listening")
# Listen for incoming datagrams

def checkUserList(name):
    for i in users:
        if i["handle"] == name:
            return False
    return True

def checkUserAddress(address):
    for i in users:
        if i["address"] == address:
            return i["handle"]
    return 0

def checkUserName(handle):
    for i in users:
        if i["handle"] == handle:
            return i["address"]
    return 0

def allUsers():
    names = ['List of users in the server:']
    for i in users:
        names.append(i["handle"])

    return names

def checkChannel(channelName):
    for channel in channels:
        if channel['name'] == channelName:
            return channel
    return 0

def checkChannelUsers(channel, name):
    for index in range(len(channels)):
        if channels[index]['name'] == channel:
            for x in range(len(channels[index]['users'])):
                if name == channels[index]['users'][x]['handle']:
                    return channels[index]['users'][x]
    return 0

def allChannels():
    names = ['List of channels in the server:']
    for i in channels:
        names.append(i["name"])

    return names


def received(message):
    load = json.loads(message[0])
    print(load)
    #message[0] is the sent data
    #message[1] is the address tuple

    match load["command"]:
        case "join":
            msg = json.dumps({"message":"Connection to the Message Board Server is successful!"})
            sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
            return True

        case "leave":
            name = checkUserAddress(message[1])
            if not checkUserList(name):
                for index in range(len(users)):
                    if users[index]['handle'] == name:
                        del users[index]
                        break

            for index in range(len(channels)):
                for x in range(len(channels[index]['users'])):
                    if channels[index]['users'][x]['handle'] == name:
                        del channels[index]['users'][x]
                        break

            msg = json.dumps({"message":"Connection closed. Thank you!"})
            sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
            return True
        
        case "register":

            #Checks if sender is already registered, if yes, send error
            if checkUserAddress(message[1]) != 0:
                msg = json.dumps({"message":"Error: Registration failed. You already registered"})
                sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                print("Address already exists")

            #Else if handle doesn't exist, register the sender
            elif (checkUserList(load["handle"])):
                msg = json.dumps({"message":"Welcome {}!".format(load["handle"])})
                users.append({"handle" : load["handle"], "address" : message[1]})
                sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                print("A user has been registered")
            
            #Else if handle already exists, send error
            else:
                msg = json.dumps({"message":"Error: Registration failed. Handle or alias already exists."})
                sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                print("Username already exists")
            return True

        case "all":
            handle = checkUserAddress(message[1])
            if (handle != 0):
                msg = json.dumps({"message":"{}: {}".format(handle, load["message"])})

                for user in users:
                    sockServer.sendto(bytes(msg, encoding="utf-8"), user["address"])
                print("sent message to all")

            else:
                msg = json.dumps({"message":"Error: Register first"})
                sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
            return True
                
        case "msg":
            sender = checkUserAddress(message[1]) #Getting name of sender
            address = checkUserName(load["handle"]) #Getting address of receiver

            if (address != 0 and sender != 0):
                msgSender = json.dumps({"message":"[To {}]: {}".format(load["handle"], load["message"])})
                msgReceiver = json.dumps({"message":"[From {}]: {}".format(sender, load["message"])})

                sockServer.sendto(bytes(msgSender, encoding="utf-8"), message[1])
                sockServer.sendto(bytes(msgReceiver, encoding="utf-8"), address)
            elif(address == 0):
                msg = json.dumps({"message":"Error: Handle or alias doesn't exist"})
                sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])

            elif(sender == 0):
                msg = json.dumps({"message":"Error: Register First"})
                sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])

            elif(sender == 0 and address == 0):
                msg = json.dumps({"message":"Error: Register first and the receiver user doesn't exist"})
                sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
            return True

        case "users":
            if len(users) == 0:
                msg = json.dumps({"message":"There are no users"})
            
            elif len(users) == 1:
                msg = json.dumps({"message":users[0]["handle"]})

            else:
                currentUsers = allUsers()
                all = "\n".join(currentUsers)
                msg = json.dumps({"message": all})

            sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
            print("Gave list of users")
            return True
        
        case "close":
            msg = json.dumps({"message":"Connection closed. Thank you!"})
            sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
            print("Server will be closed. Goodbye!")
            return False

        #Channels
        case "new_ch":
            sender = checkUserAddress(message[1])
            #Checks if sender is already registered, if not, send error
            if sender == 0:
                msg = json.dumps({"message":"Error: Channel creation failed. You must register first"})
                sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                print("User should register first before creating a channel")

            #Else if sender is registered, check the channel name
            else:
                #If new channel, channel is created and user will join
                if checkChannel(load["channel"]) == 0:
                    msg = json.dumps({"message":"Channel:Created new channel! Welcome " + sender + " to " + load["channel"] + "!", 'channel' : load['channel']})
                    channels.append({"name" : load["channel"], "users" : [{'handle' : sender, 'address': message[1]}]})
                    sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                    print("A new channel has been created")
                else:
                    #Else if channel already exists, send error
                    msg = json.dumps({"message":"Error: Channel creation failed. Channel name already exists."})
                    sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                    print("Channel name already exists")
            return True

        case "join_ch":
            sender = checkUserAddress(message[1])
            channelName = load["channel"]
            channel = checkChannel(channelName)
            channelUser = checkChannelUsers(channelName, sender)

            if sender == 0:
                msg = json.dumps({"message":"Error: Attempt to join channel failed. You must register first"})
                sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                print("User should register first before joining a channel")

            #Else if sender is registered, check the channel name
            else:
                #If channel doesn't exist, send error
                if channel == 0:
                    msg = json.dumps({"message":"Error: Channel doesn't exist."})
                    sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                    print("Channel doesn't exist")
                
                #Else if channel exists, the user will attempt to join
                else:
                    #if user doesn't exist in channel, user will join
                    if channelUser == 0:
                        msg = json.dumps({"message":"Channel:Welcome " + sender + " to " + load["channel"] + "!", 'channel' : load['channel']})
                        
                        for index in range(len(channels)):
                            if channels[index]['name'] == channelName:
                                channels[index]['users'].append({'handle' : sender, 'address' : message[1]})
                        sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                        print("User joined channel")

                    #If user is already in channel, send error
                    else:
                        msg = json.dumps({"message":"Error: Attempt to join channel failed. You already joined"})
                        sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                        print("User already part of channel")
            return True

        case "leave_ch":
            sender = checkUserAddress(message[1])
            channelName = load["channel"]
            channel = checkChannel(channelName)
            channelUser = checkChannelUsers(channelName, sender)

            if sender == 0:
                msg = json.dumps({"message":"Error: Attempt to leave channel failed. You must register first"})
                sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                print("User should register first before leaving a channel")

            #Else if sender is registered, check the channel name
            else:
                #If channel doesn't exist, send error
                if channel == 0:
                    msg = json.dumps({"message":"Error: Channel doesn't exist."})
                    sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                    print("Channel doesn't exist")
                
                #Else if channel exists, the user will attempt to leave
                else:
                    #if user doesn't exist in channel, send error
                    if channelUser == 0:
                        msg = json.dumps({"message":"Error: Attempt to leave channel failed. You are not part of this channel"})
                        sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                        print("User not part of channel")

                    #If user is already in channel, user will leave
                    else:
                        msg = json.dumps({"message": "Channel:Goodbye! " + sender + " left " + load['channel'], "channel" : load['channel']})
                        for index in range(len(channels)):
                            if channels[index]['name'] == channelName:
                                for x in range(len(channels[index]['users'])):
                                    if channels[index]['users'][x]['handle'] == sender:
                                        del channels[index]['users'][x]
                                        break
                        sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                        print("User left channel")
                return True

        case "msg_ch":
            sender = checkUserAddress(message[1])
            channelName = load["channel"]
            channel = checkChannel(channelName)
            channelUser = checkChannelUsers(channelName, sender)

            if sender == 0:
                msg = json.dumps({"message":"Error: Attempt to message channel failed. You must register first"})
                sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                print("User should register first before leaving a channel")

            #Else if sender is registered, check the channel name
            else:
                #If channel doesn't exist, send error
                if channel == 0:
                    msg = json.dumps({"message":"Error: Channel doesn't exist."})
                    sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                    print("Channel doesn't exist")
                
                #Else if channel exists, the user will attempt to message
                else:
                    #if user doesn't exist in channel, send error
                    if channelUser == 0:
                        msg = json.dumps({"message":"Error: Attempt to message channel failed. You are not part of this channel"})
                        sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
                        print("User not part of channel")

                    #If user is already in channel, user will message
                    else:
                        msg = json.dumps({"message": "Channel (" + load['channel'] + ") - {}: {}".format(sender, load["message"]), "channel" : load['channel']})

                        for user in channel['users']:
                            sockServer.sendto(bytes(msg, encoding="utf-8"), user["address"])
                        print("sent message to all")
            return True
        
        case "server_ch":
            if len(channels) == 0:
                msg = json.dumps({"message":"There are no channels"})
            
            elif len(channels) == 1:
                msg = json.dumps({"message":channels[0]["name"]})

            else:
                currChannels = allChannels()
                all = "\n".join(currChannels)
                msg = json.dumps({"message": all})

            sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
            print("Gave list of channels")
            return True

        case other:
            msg = json.dumps({"message":"Incompatible command"})
            sockServer.sendto(bytes(msg, encoding="utf-8"), message[1])
            print("Incompatible command")
            return True



            




    


while(stopper):
    try:
        message = sockServer.recvfrom(bufferSize)
        stopper = received(message)
    except socket.error:
        continue





