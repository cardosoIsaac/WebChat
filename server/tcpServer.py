import socket
import threading
from random import *
import time


#*************************************************************************************
#Main()
def main():
    host = '127.0.1.1'
    port = 5000

    #list of threads/connections and their socket             
    connections = {}
    #list of clients currently in a chat session
    #with another client
    busyClients = {}




    #**********************************************************************************
    #This function verifies if the client ID is on the list of subscribers.
    #Returns true if it is, else returns false.
    def isRegistered(clientID):
        bool = False
        file = open("ClientID-List", "r")
        for line in file:
            id = line.replace('\n', '')
            if id == clientID:
                bool = True
                break
        return bool
    #End of isRegistered()
    #**********************************************************************************
    



    #**********************************************************************************
    #This functions checks if a certain client on the busyClients list.
    #Meaning the client is busy in a chat session with another user.
    def isBusy(clientID):
        bool = False
        for key in busyClients:
            if key == clientID:
                bool = True
                break
        return bool
    #End of isBusy()
    #**********************************************************************************




    #**********************************************************************************
    #This function checks if a certain client is on the list of connected clients
    def isConnected(clientID):
        bool = False
        for key in connections:
            if key == clientID:
                bool = True
                break
        return bool
    #End of isConnected()
    #**********************************************************************************




    #**********************************************************************************
    #This function is called everytime a new client connects to the server.
    #It calls on other functions to validate the connection, it responds to 
    #client requests, and closes the connections when it is done.
    def newClient(clientSocket, addr):
        while True:
            #Split recieving data into request and id
            data = clientSocket.recv(1024)

            if not data:
                break

            data = data.decode()
            request = data.split()[0]
            id = data.split()[1]

            #new connection request
            if request == "HELLO":
                print ("\nEstablishing connection with Client-ID " + id + "...")

                #call definition to check if client is on list of subscribers
                #if so, send CONNECTED message to client
                if isRegistered(id):
                    data = "CONNECTED"
                    print (data)
                    clientSocket.send(data.encode())

                    #add clientsocket to list of connections
                    connections[id] = clientSocket
                    print("\n")
                  
                    #wait for a client request
                    while True:
                        data = clientSocket.recv(1024)

                        if not data:
                            break

                        data = data.decode()

                        #get request from data
                        request = data.split()[0]

                        #start a new chat with another client
                        if request == "CHAT_REQUEST":
                            chatWithUserID = data.split()[1]

                            #check if chatWithUserID requested is connected and not busy
                            if isConnected(chatWithUserID) and not isBusy(chatWithUserID):
                                #generate a sessionID
                                sessionID  = randint(100000, 999999) 
                                #add pair of clients to list of busy clients
                                busyClients[id] = (sessionID, chatWithUserID)
                                busyClients[chatWithUserID] = (sessionID, id)

                                #Get chatWithUserID's socket
                                chatWithUserIDSocket = connections.get(chatWithUserID)

                                #Display Chat started messege to both clients
                                data = "CHAT_STARTED " + str(sessionID) + " " + str(chatWithUserID)
                                clientSocket.send(data.encode())
                                data = "CHAT_STARTED " + str(sessionID) + " " + str(id)
                                chatWithUserIDSocket.send(data.encode())

                            else:
                                data = "UNREACHABLE"
                                clientSocket.send(data.encode())

                        #received a chat message to be sent to another user. Extract destination ID
                        #and compose a chat message and send it to the other user
                        elif request == "CHAT_MESSAGE":
                            sendTo = data.split()[1]
                            sessionID = data.split()[2]
                            chatWithUserIDSocket = connections.get(sendTo)
                            message = "CHAT " + data[18:]
                            chatWithUserIDSocket.send(message.encode())

                            #open files where messages are being stored and append this message
                            try:
                                fname = str(id) + "-" + str(sendTo)
                                f1 = open(fname, "a+")
                                fname = str(sendTo) + "-" + str(id)
                                f2 = open(fname, "a+")

                                message = "From " + str(id) + ":" + data[18:]
                                f1.write(message + "\n")
                                f2.write(message + "\n")

                                f1.close()
                                f2.close()
                            except IOError:
                                print("Error opening or appending data to file.")

                        #received an end request from user. Send end request to the other user 
                        #and removed them from list of busy clients
                        elif request == "END_REQUEST":
                            sendTo = data.split()[1]
                            message = "END_NOTIF"
                            chatWithUserIDSocket = connections.get(sendTo)
                            chatWithUserIDSocket.send(message.encode())

                            del busyClients[id]
                            del busyClients[sendTo]

                        #received a timeout request. Send an end notification to the user
                        #and remove the user from the list of busy clients
                        elif request == "TIMEOUT":
                            message = "END_NOTIF"
                            clientSocket.send(message.encode())

                            del busyClients[id]

                        #look up and send history messages between
                        #client making the rquest and the specified
                        #client
                        elif request == "HISTORY_REQ":
                            userID = data.split()[1]
                            fname = str(id) + "-" + str(userID)

                            #open file to read history messages from and send each line
                            # as a history response. Close the file when done.
                            try:
                                file = open(fname, "r")
                                if file.mode == "r":
                                    f = file.readlines()
                                    for x in f:
                                        data = "HISTORY_RESP " + x
                                        clientSocket.send(data.encode())
                                        time.sleep(.01)
                                    file.close()
                            except IOError:
                                print("Error: Failed to open file.")


                        #Client disconnected. Close socket and exit
                        else:
                            print("\n" + str(addr) + "\nDisconnecting...")
                            #remove client from connections list
                            del connections[id]
                            clientSocket.close()
                            exit()

                #client was not on the list of subscribers
                else:
                    data = "DECLINED"
                    print (data)
                    clientSocket.send(data.encode())
                    clientSocket.close()
                    exit()
        try:
            print("Disconnecting client-ID " +  str(id))
            del connections[id]
        except UnboundLocalError:
            print()
        clientSocket.close()
        exit()
    #End of newClient()
    #**********************************************************************************
    



    #**********************************************************************************
    #Accept new connections and start a new thread for each one.

    #Create a welcome TCP socket 
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host,port))
    sock.listen(1)

    print ("Ready to serve...")

    while True:
        c, addr = sock.accept()
        print ("\nConnection from: " + str(addr))
        t = threading.Thread(target=newClient, args=(c, addr))
        t.start()

    sock.close()
    exit()
#****End of Main()  
    #**********************************************************************************    

#call main
main()
