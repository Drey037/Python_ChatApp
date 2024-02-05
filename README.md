# Python ChatApp
Chat room application that uses python sockets

**Note: This program works on Python version 3.10**

## Getting Started

### Prerequisites
- Python 3.10 should be installed on your system.

### Running the Application
1. Open three command line interfaces (CLI).
2. Navigate to the project directory in each CLI.

#### Starting the Server
- In one CLI, run the command:
```bash
python server.py
```
#### Starting the Clients
- In the second and third CLI, run the command:
```bash
python client.py
```

#### Joining a Server
- In the client GUI, type the command:
```/join 127.0.0.1 12345```
- Press Enter.

#### Registration
- After joining, register yourself with a handle or nickname using the command:
/register <Handle or nickname>

## Available Commands to use on Client GUI
- `/join <IP Address> <Port>`: Join a server by providing the IP address and port number.
- `/leave`: Leave the current server.
- `/register <Handle or nickname>`: Register yourself with a handle or nickname on the server.
- `/all <Message>`: Send a message to all users registered on the server.
- `/msg <Handle or nickname> <Message>`: Send a direct message to a specific user on the server.
- `/close`: Close the server.
- `/users`: Show a list of registered users on the server.
- `/?`: Show a list of available commands.
- `/emojis`: Show a list of available emojis.
- `/new_ch <channel name>`: Create a new channel on the server.
- `/join_ch <channel name>`: Join a specific channel on the server.
- `/leave_ch <channel name>`: Leave a specific channel on the server.
- `/msg_ch <channel name> <message>`: Send a message to a specific channel on the server.
- `/server_ch`: Show a list of all channels on the server.
- `/user_ch`: Show a list of channels joined by the user.
