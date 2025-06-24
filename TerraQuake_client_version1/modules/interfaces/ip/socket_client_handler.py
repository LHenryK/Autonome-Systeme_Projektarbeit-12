import threading
import socket

class ClientHandler(threading.Thread):
    def __init__(self, serverAddress: str, serverPort: int) -> None:
        threading.Thread.__init__(self)
        self.serverAddress: str = serverAddress
        self.serverPort: int = serverPort

        self.clientSocket = socket.socket()

        self.serverCallbackFunc = None
        
        self.clientConnHandler = None

        self.isClientAlive = True
    
    def run(self) -> None:
        print("Connecting ...")
        
        try:
            self.clientSocket.connect((self.serverAddress, self.serverPort))
        except:
            print("The conneciton to the server was refused")
            return
        
        while self.isClientAlive:
            data = self.clientSocket.recv(131072).decode()
            if data != None:
                self.serverCallbackFunc(str(data))
    
    def disconnect(self) -> None:
        self.isClientAlive = False
        self.clientSocket.close()

    def setCallback(self, callback) -> None:
        self.serverCallbackFunc = callback
