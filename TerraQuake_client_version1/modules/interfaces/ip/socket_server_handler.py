import threading
import socket

class Client:
    def __init__(self, conn: socket.socket, address, thread: object) -> None:
        self.clientConn: socket.socket = conn
        self.clientAddress = address
        self.clientThread: threading.Thread = thread


class ServerHandler:
    def __init__(self, address: str, port: int) -> None:
        self.serverAddress: str = address
        self.serverPort: int = port

        self.clientList: list[Client] = []
        
        self.serverSocket = socket.socket()

        self.serverSocket.bind((self.serverAddress, self.serverPort))

        self.serverSocket.listen(2)

    def start(self) -> None:
        print("Waiting for incoming connections ...")
        
        while True:
            newClientConn, newClientAddress = self.serverSocket.accept()
            print("New incoming connection !!!")

            newClientThread = threading.Thread(target=ServerConnectionHandler, args=(newClientConn, newClientAddress, self.clientCallback))
            
            # Add new client to client list
            newClientObj = Client(newClientConn, newClientAddress, newClientThread)
            self.clientList.append(newClientObj)

            newClientThread.start()
            newClientThread.join()
    
    def stop(self) -> None:
        print("Stoping server ...")
        self.serverSocket.close()

    def getClientByThreadID(self, threadId)->Client:
        print("Finding Thread ID")
        for i in self.clientList:
            if(i.clientThread.ident == threadId):
                print("Found Thread ID")
                return i
        return None

    def clientCallback(self, threadId: int, contents: str):
        print("Got Callback")
        client = self.getClientByThreadID(threadId)
        if client != None:
            print(f"Got request from {str(client.clientAddress)} \n")
            print(contents)

    def sendClients(self, dataString: str) -> None:
        for i in self.clientList:
            i.clientConn.send(dataString.encode())



class ServerConnectionHandler(threading.Thread):
    def __init__(self, socketConn: socket.socket, address, requestCallbackFunc):
        threading.Thread.__init__(self)
        self.clientSocketConn: socket.socket = socketConn
        self.clientAddress = address
        self.clientCallbackFunc = requestCallbackFunc

        self.run()

    def run(self):
        print("Run Loop")
        while True:
            data = self.clientSocketConn.recv(1024).decode()
            if data != None:
                print("Got Data!")
                
                print(threading.get_ident())
                # if data is received
                self.clientCallbackFunc(threading.get_ident(), str(data))