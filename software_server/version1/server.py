import socket
import ssl
import threading
import sys # Added for sys.stdout.flush() if needed for immediate output

host = '0.0.0.0'
# Hier den Richtigen Port eintragen:
port = 123456

# SSL-Kontext erstellen
# Ensure these paths are correct and accessible by the user running the script
try:
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(certfile="/etc/letsencrypt/live/[Domain Name]/fullchain.pem",
                            keyfile="/etc/letsencrypt/live/[Domain Name]/privkey.pem")
    # Optional: Configure SSL for more security (e.g., specific ciphers, minimum TLS version)
    # context.set_ciphers('HIGH:!aNULL:!MD5')
    # context.minimum_version = ssl.TLSVersion.TLSv1_2
except FileNotFoundError:
    print("Error: SSL certificate or key file not found. Please check paths:")
    print("  Cert file: /etc/letsencrypt/live/[Domain Name]/fullchain.pem")
    print("  Key file: /etc/letsencrypt/live/[Domain Name]/privkey.pem")
    sys.exit(1) # Exit if SSL setup fails, as it's critical for this server
except ssl.SSLError as e:
    print(f"Error loading SSL certificate chain: {e}")
    sys.exit(1)

# List to keep track of all active client sockets (SSL-wrapped sockets)
# This list needs to be accessible by all client handler threads.
clients = []
clients_lock = threading.Lock() # A lock to protect the 'clients' list

def broadcast_message(message_bytes, sender_socket=None):
    """Sends a message to all connected clients."""
    with clients_lock: # Acquire the lock before iterating through the shared list
        # Iterate over a copy to avoid issues if clients list changes during iteration
        for client_ssl_socket in list(clients):
            if client_ssl_socket != sender_socket: # Optional: Don't send the message back to the sender
                try:
                    client_ssl_socket.sendall(message_bytes)
                except ssl.SSLError as e:
                    print(f"SSL Error sending to client {client_ssl_socket.getpeername()}: {e}. Removing broken client.")
                    clients.remove(client_ssl_socket)
                except Exception as e:
                    print(f"Error sending to client {client_ssl_socket.getpeername()}: {e}. Removing broken client.")
                    # If sending fails, assume the client is no longer active and remove it
                    clients.remove(client_ssl_socket)

def handle_client(conn, client_address):
    # 'conn' here is the SSL-wrapped socket (secure_conn)
    # Add the new client to the global list
    with clients_lock: # Acquire the lock before modifying the shared list
        clients.append(conn)
    print(f"Accepted secure connection from {client_address}. Total clients: {len(clients)}")

    try:
        # Set a timeout for the client's socket within the thread.
        # This prevents recv() from blocking indefinitely if a client disappears without closing.
        # You can adjust this timeout value as needed.
        conn.settimeout(30.0) # 30-second timeout for recv operations

        while True:
            try:
                data = conn.recv(131072)
                if not data:
                    print(f"Client {client_address} disconnected gracefully.")
                    break # Exit the loop if client disconnects
            except ssl.SSLWantReadError: # Occurs if SSL handshake or re-negotiation needs more data
                # This is common in non-blocking or timeout scenarios with SSL
                # You might need a small delay here in a very tight loop, or re-structure
                # to handle non-blocking SSL operations more robustly.
                # For a blocking socket with timeout, it usually means the timeout occurred.
                print(f"SSLWantReadError for {client_address}. Retrying recv...")
                continue
            except socket.timeout:
                print(f"Client {client_address} timed out waiting for data. Removing from active clients.")
                break # Break out of loop if timeout occurs
            except ssl.SSLError as e:
                print(f"SSL Error receiving from {client_address}: {e}. Disconnecting client.")
                break # Break out of loop on SSL errors
            except Exception as e:
                print(f"General error receiving from {client_address}: {e}. Disconnecting client.")
                break # Break out of loop on other errors

            try:
                message = data.decode('utf-8')
            except UnicodeDecodeError:
                print(f"UnicodeDecodeError from {client_address}. Received non-UTF-8 data: {data[:50]}...")
                continue # Skip this message and wait for next
            except Exception as e:
                print(f"Error decoding message from {client_address}: {e}. Disconnecting client.")
                break

            print(f"Received message from {client_address}: '{message}'")

            # --- BROADCASTING LOGIC ---
            # Send the received message to all currently connected clients
            # (excluding the sender by default in broadcast_message if sender_socket is passed)
            broadcast_message(message.encode('utf-8'), conn)

    except Exception as e:
        print(f"Unhandled error in handle_client for {client_address}: {e}")
    finally:
        # Remove the client from the list when the connection is closed or an error occurs
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        try:
            conn.shutdown(socket.SHUT_RDWR) # Attempt to gracefully shutdown the SSL connection
            conn.close() # Close the underlying socket
        except Exception as e:
            print(f"Error closing connection for {client_address}: {e}")
        print(f"Client {client_address} connection handler finished. Remaining clients: {len(clients)}")


# Server-Socket erstellen
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow reuse of address for quicker restarts

try:
    server_sock.bind((host, port))
    server_sock.listen(5) # Listen for up to 5 pending connections
    print(f"Server wartet auf Verbindungen unter {host}:{port} mit SSL...")

    while True:
        client_socket, client_address = server_sock.accept() # Accepts raw TCP connection
        print(f"Accepted raw connection from {client_address}")

        try:
            # Wrap the client socket with SSL/TLS
            secure_conn = context.wrap_socket(client_socket, server_side=True)
            print(f"SSL handshake successful with {client_address}")

            # Start a new thread to handle the secure client connection
            client_handler = threading.Thread(target=handle_client, args=(secure_conn, client_address))
            client_handler.start()
        except ssl.SSLError as e:
            print(f"SSL handshake failed with {client_address}: {e}")
            client_socket.close() # Close the raw socket if handshake fails
        except Exception as e:
            print(f"Error processing connection from {client_address}: {e}")
            client_socket.close() # Ensure socket is closed on any other error

except KeyboardInterrupt:
    print("\nServer shutting down due to user interrupt (Ctrl+C).")
except Exception as e:
    print(f"Server error: {e}")
finally:
    print("Server cleanup.")
    # Close the main server socket
    if server_sock:
        server_sock.close()
    
    # Close all remaining client sockets
    with clients_lock:
        for client_ssl_socket in list(clients): # Iterate over a copy
            try:
                client_ssl_socket.shutdown(socket.SHUT_RDWR)
                client_ssl_socket.close()
            except Exception as e:
                print(f"Error closing client socket during shutdown: {e}")
    print("All sockets closed. Server has stopped.")