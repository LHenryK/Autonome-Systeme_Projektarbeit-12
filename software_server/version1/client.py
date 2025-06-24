import threading
import socket
import ssl
import sys

from os import system, name

host = "Hier Server IP Eintragen!"
# Hier den Richtigen Port eintragen:
port = 123456

messageList: list = []


# SSL-Kontext erstellen
client_context = ssl.create_default_context()

try:
    client_context.load_cert_chain(
        certfile="ssl/[Client Zertifikat einfügen", # Ihr client_cert.pem vom Client
        keyfile="ssl/[Client Key einfügen].pem"    # Ihr client_key.pem vom Client
    )
    print("Client-Zertifikat und privater Schlüssel geladen.")
except FileNotFoundError:
    print("FEHLER: client_cert.pem oder client_key.pem nicht gefunden.")
    print("Stellen Sie sicher, dass sie im selben Verzeichnis sind oder geben Sie den vollen Pfad an.")
    sys.exit(1)


client_context.check_hostname = True
client_context.verify_mode = ssl.CERT_REQUIRED  # In der Praxis Zertifikate validieren!


def handle_server(server_socket, callback):
    data = server_socket.recv(1024)
    response = data.decode('utf-8')
    if response[:2] == "42":
        messageList.append(response)
        callback(response)

def onNewMessage(msg):
    print("-> " + msg)    


secure_client_sock = None

try:
    # Client-Socket erstellen
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    print("Attempting to connect...") # Added for debugging

    # Sichere Verbindung herstellen
    secure_client_sock = client_context.wrap_socket(client_sock, server_hostname=host)
    secure_client_sock.connect((host, port))

    print("Connection successful!") # This will only print if connect succeeds

    client_handler = threading.Thread(target=handle_server, args=(secure_client_sock, onNewMessage,))
    client_handler.start()

    print("Send now messages!")

    while True:
        print("Inside loop, about to ask for input...")
        
        message = input("Enter your message: ")
        print(f"User entered: {message}") # Confirm input was received
        
        secure_client_sock.send(str("54"+message).encode('utf-8'))
        print("Message sent.")
        

except ConnectionRefusedError:
    print(f"Error: Connection refused. Is the server running on {host}:{port}? "
          f"Also check firewalls.")
except ssl.SSLError as e:
    print(f"SSL Error during connection: {e}")
    print("Common reasons: Server certificate is self-signed/not trusted, or hostname mismatch.")
    print("If you are using a self-signed cert for testing, you might need to load it explicitly or adjust verify_mode.")
except socket.gaierror:
    print(f"Error: Hostname '{host}' could not be resolved. Check the host name.")
except socket.timeout: # Explicitly catch timeout
    print(f"Error: Connection attempt to {host}:{port} timed out. Server might be down or unreachable.")
except Exception as e:
    print(f"An unexpected error occurred during connection or communication: {e}")
finally:
    if secure_client_sock:
        try:
            secure_client_sock.close()
            print("Socket closed.")
        except Exception as e:
            print(f"Error closing socket: {e}")
