import sys
import socket
import threading
import queue
import time

#global timer variable
t = 15
#global timerOff to stop timer when user ends the chat
timerOff = False
#******************************************************************************
#Countown timer using global variable timer
def activity_timer(input_queue):
	global t
	while t > 0 and not timerOff:
		t -= 1
		time.sleep(1)

	#if time out(t <= 0) add an "End chat" to the queue to end current chat
	#and reset the timer
	if t == 0:
		input_queue.put("TIMEOUT")
	#reset timer
	t = 15
#******************************************************************************



#******************************************************************************
#Definition to get user input in a nonstopping loop
def user_input(input_queue):
	#keep asking user for input and add it to the queue
	while True:
		input_queue.put(sys.stdin.readline())

#******************************************************************************


#******************************************************************************
#Definition to always listen for server messages
def incoming_server_messages(input_queue, s):
	#receive incoming messages from server
	while True:
		message = s.recv(1024)
		if not message:
			break

		#decode the message and add it to the queue
		input_queue.put(message.decode())
#******************************************************************************


#******************************************************************************
def main():

	#host and port of the server to connect to
	host = '127.0.1.1'
	port = 5000

	#flags  that are set to true when user is logged on and in a chat session
	inChat = False
	loggedOn = False
	sendTo = 0

	#using global t and timerOff for timer
	global t
	global timerOff


	#Create a TCP socket and connect to the server
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host,port))


	#Queue to store server messages and user commands
	input_queue = queue.Queue()

	#Start a thread that listens for incoming messages
	listeningThread = threading.Thread(target = incoming_server_messages, args=(input_queue,s))
	listeningThread.daemon = True
	listeningThread.start()

	#start a thread that gets user input
	inputThread = threading.Thread(target=user_input, args=(input_queue,))
	inputThread.daemon = True
	inputThread.start()

	print("Type 'Log on' to log on or 'q' to quit the program: ")

	#Get the next item from the queue, parse it and do accordingly
	while True:
		if not input_queue.empty():
			option = input_queue.get()

			#ignore empty input
			if option == "\n":
				continue

			#replace the new line symbol with a space except for a 
			#history response
			if not option.split()[0] == "HISTORY_RESP":
				option = option.replace('\n','')

			#'q,' exit the loop
			if option == 'q':
				break

			#"Log off," exit the the loop
			elif option == "Log off":
				loggedOn = False
				break

			#if "Log on," get user id from file if it exists and send a HELLO request to server.
			#if file does not exisits, display message and exit the loop.
			elif option == "Log on":
				#if user is not already logged on
				if not loggedOn:
					try:
						file = open("Client-ID", 'r')
						myID = file.read().replace('\n','')
						request = "HELLO " + str(myID)
						s.send(request.encode())
					except FileNotFoundError:
						print("You do not have the right credentials to access the chat")
						break

			#"CONNECTED," server has verified the user's credentials. Display instructions.
			#set loggedOn flag to True
			elif option == "CONNECTED":
				loggedOn = True
				print("Connected\n")
				print("You are now connected to the chat")
				print("To start a chat with another user type, 'Chat Client-ID'")
				print("To see past messages from last chat type, History Client-ID")
				print("('Client-ID' is the user you want to chat with)")

			#"Declined," server could not verify the user's credentials. Exit the loop
			elif option == "DECLINED":
				print("Declined")
				break

			#if first word of command is "Chat," second word should be the client-id of the user
			#this user wants to chat with. Compose CHAT_REQUEST and send it to the server
			elif option.split()[0] == "Chat":
				#if user is not currently in a chat session
				if not inChat:
					try:
						chatWith = option.split()[1]
						request = "CHAT_REQUEST " + str(chatWith)
						s.send(request.encode())
					except IndexError:
						print("Invalid Chat command format! Try again.")

			#"UNREACHABLE," the other client is either busy or not connected.
			elif option == "UNREACHABLE":
				print("Correspondent Unreachable")

			#received a chat started notification from server. Display options and set 
			#inChat flag to true
			elif option.split()[0] == "CHAT_STARTED":
				#start the timer
				timerOff = False
				timer_thread = threading.Thread(target=activity_timer, args=(input_queue,))
				timer_thread.daemon = True
				timer_thread.start()

				currentSessionID = option.split()[1]
				otherUser = option.split()[2]
				print("Chat started")
				print("********************************************************************")
				print("You are now in a chat session with user: " + str(otherUser))
				print("SessionID: " + str(currentSessionID))
				print("To end the chat type, 'End chat'\n")
				print("Chat session will end after 15 seconds if there is no activity.")
				inChat = True
				sendTo = otherUser

			#received a chat message from another user. Display the message.
			elif option.split()[0] == "CHAT":
				#reset timer
				t = 15
				message = option[6:]
				print(message)

			#received end notification from server. Display chat ended
			elif option == "END_NOTIF":
				inChat = False
				timerOff = True
				print("Chat ended")
				print("********************************************************************")

			#user wants to end the chat. Display chat ended and send an END_REQUEST to the server
			#and set inChat flag to false
			elif option == "End chat":
				#if user is in a chat session
				if inChat:
					request = "END_REQUEST " + sendTo
					s.send(request.encode())
					inChat = False
					timerOff = True
					print("Chat ended")
					print("********************************************************************")

			#activity_timer expired. compose a TIMEOUT request and send it to the server
			elif option == "TIMEOUT":
				request = option
				s.send(request.encode())

			#user requested to see past message with a specific user. Compose a HISTORY_RQUEST
			#and send it to the server.
			elif option.split()[0] == "History":
				otherUser = option.split()[1]
				request = "HISTORY_REQ " + str(otherUser)
				s.send(request.encode())

			#received a history response. Extract the message and display it to the user
			elif option.split()[0] == "HISTORY_RESP":
				message = option[13:]
				print(message)

			#if user is currently in a chat session, compose a CHAT_MESSAGE request and send it
			#to the server.
			else:
				if inChat:
					#reset timer
					t = 15
					message = option
					request = "CHAT_MESSAGE " + str(sendTo) + " " + message
					s.send(request.encode())


	#close tcp connection and exit
	print("Goodbye")
	s.close()
	exit()

#call main 
main()
