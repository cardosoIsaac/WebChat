# WebChat
Web chat using TCP sockets and multithreading in Python.

The client side program assumes there is a file with a Client ID stored locally.
When the client logs in, the server then checks to see if the ClientID is in the ClientID-List file. 
If it's there, the server starts a connection with this client. The chat ends when the user chooses to or when a time out occurs. 

***********************************************************************************************************************************
## Run Program
To start the server make sure you have python 3 installed. Then run the following command on the command line interface:

`python tcpServer.py`

To run the client side program run the following command:

`python tcpClient.py`

***********************************************************************************************************************************
## Protocol Messages Syntax Definitions
These are the messages the client program sends to the server and vice versa 

**HELLO <Client-ID-A>:** Initiates the process for client A to be connected to the server. Client-ID-A is the user’s unique client ID.

**CONNECTED:** Sent by the server to notify the client has been connected.

**DECLINED:** Sent by the server to notify the client that the server could not validate the user’s Client-ID or if some other error occurred while trying to connect.

**CHAT_REQUEST <Client-ID-B>:** Sent by Client A to the server to request a chat session with Client B.

**CHAT_STARTED <Session-ID> <Client-ID-B>:** Sent by the server to notify Client A that a chat session has started with Client B.

**UNREACHABLE:** Sent by the server to notify Client A that Client B could not be reached.

**END_REQUEST <Client-ID-B>:** Sent by Client A to the server to request to end the chat session.

**END_NOTIF:** Sent by the server to notify Client B that Client A has ended the chat.

**CHAT <message/>:** Sent by the server to Client A which includes the message sent by Client B.

**HISTORY_REQ <Client-ID-B>:** Sent by Client A to request the server to send all the past messages with Client B.

**HISTORY_RESP <message/>:** Sent by the server to Client A which includes a message stored in the last chat session file.

**TIMEOUT:** Sent by Client A to notify the server that a timeout has occurred and to end the chat.

