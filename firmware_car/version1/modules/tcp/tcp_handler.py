import threading
import socket
import ssl
import sys

from os import system, name


class TCPHandler(threading.Thread):
    serverHost: str
    serverPort: int
    
    ssl_cert_file: str
    ssl_key_file: str

    client_context: ssl.SSLContext
    client_socket: ssl.SSLSocket

    currentMsg: str
    isRecevingMsg: bool


    def __init__(self, host: str, port: int, ssl_cert_file: str, ssl_key_file: str, recCallbackFunc, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.serverHost = host
        self.serverPort = port

        self.ssl_cert_file = ssl_cert_file
        self.ssl_key_file = ssl_key_file

        self.recCallbackFunc = recCallbackFunc

        self.initSSL()
        self.initSecSocket()
    
    def initSSL(self):
        self.client_context = ssl.create_default_context()
        
        try:
            self.client_context.load_cert_chain(
                certfile=self.ssl_cert_file,
                keyfile=self.ssl_key_file
            )
        
        except FileNotFoundError:
            # Raise exception for fileNotFoundError handling ...
            pass

        self.client_context.check_hostname = True
        self.client_context.verify_mode = ssl.CERT_REQUIRED
    
    def initSecSocket(self):
        try:
            new_client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            self.client_socket = self.client_context.wrap_socket(new_client_sock, server_hostname=self.serverHost)
            # self.client_socket.settimeout(5.0)
            self.client_socket.connect((self.serverHost, self.serverPort))

        except ConnectionRefusedError:
            # Raise ConnectionRefusedError -> Try call function after X period of time
            ...
        except Exception as e:
            print(e)

    def run(self):
        self.clientSockLoop()

    def clientSockLoop(self):
        while(True):
            try:
                data = self.client_socket.recv(131072)
                
                response = data.decode('utf-8')
                if response[:2] == '73':
                    self.recCallbackFunc(response[2:])

            except socket.timeout:
                print("No data received within timeout period. Looping again...")
                # This allows the loop to continue and print "Hallo" again
                continue # Go back to the start of the while loop

            except UnicodeDecodeError:
                print("Error decoding received data. Skipping this message.")
                continue # Skip to the next iteration if data is not valid UTF-8

            except socket.error as e:
                print(f"Socket error: {e}. Breaking loop.")
                break # Critical socket error, likely connection issues

            except Exception as e:
                print(f"An unexpected error occurred: {e}. Breaking loop.")
                break # Catch any other unexpected errors

    def sendMsg(self, msg: str):
        sendingMsg = "73" + msg
        self.client_socket.sendall(sendingMsg.encode('utf-8'))